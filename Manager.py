from web3 import Web3
import json, asyncio

Path_Truffle = '/Users/yamirtainwala/Desktop/HeimdallManager/'
truffle_file = json.load(open(Path_Truffle + 'build/contracts/Heimdall.json'))
abi = truffle_file['abi']
bytecode = truffle_file['bytecode']


class Contract:
    def __init__(self, ethaddress, topladdress, usersdict, owner, depositfee, withdrawalfee, minwithdrawalamount, inProgressWithdrawal):
        self.ethAddress = ethaddress
        self.toplAddress = topladdress
        self.users = usersdict
        self.owner = owner
        self.depositFee = depositfee
        self.withdrawalFee = withdrawalfee
        self.minWithdrawalAmount = minwithdrawalamount
        self.inProgressWithdrawal = inProgressWithdrawal


class User:
    def __init__(self, toplAddress, etheramount, assetamount):
        self.toplAddress = toplAddress
        self.etherAmount = etheramount
        self.assetAmount = assetamount


class InProgressWithdrawal:
    def __init__(self, ethaddress, withdrawalamount, endingvalue, withdrawalfee):
        self.ethAddress = ethaddress
        self.withdrawalAmount = withdrawalamount
        self.endingValue = endingvalue
        self.withdrawalFee = withdrawalfee




web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

address = ""


def add_user(useraddress, usertopladdress, assetamount, etheramount, contractAddress):
    contractsinfo[contractAddress].users[useraddress] = User(usertopladdress, etheramount, assetamount)


ownerAddress = web3.eth.accounts[0]
ownerToplAddress = "123"
owneraccount = {ownerAddress: User(ownerToplAddress, 0, 0)}


#Read contract address from .txt file created by DeployContract.py
with open("HeimdallTransaction.txt","r") as f:
    data = f.read()
    toFind = "'contractAddress': "
    index1 = data.find(toFind)
    indexContractAddress = index1 + len(toFind)
    contractAddress = data[indexContractAddress:(indexContractAddress+44)]
    address = data[indexContractAddress:(indexContractAddress+44)]
    f.close()
    print(contractAddress)

###Mapping of contract address to contract object
contractsinfo = {address: Contract(address, "", {}, owneraccount, 0, 0, 0, {})}

add_user(web3.eth.accounts[1], "a", 0, 0, address)
add_user(web3.eth.accounts[2], "b", 0, 0, address)
add_user(web3.eth.accounts[3], "c", 0, 0, address)
add_user(web3.eth.accounts[4], "d", 0, 0, address)



###Handling event loops


###Function that takes events from topl contracts that creates ether in exchange for ether assets
def handle_asset_lock_event(user, assetsBurnt):

    if assetsBurnt < contractsinfo[address].users[user].assetAmount:
        contractsinfo[address].users[user].assetAmount -= assetsBurnt

    return

###Function that takes events from topl contracts that creates ether assets in exchange for ether
def handle_asset_release_event(user, assetsCreated):
    if contractsinfo[address].users[user].etherAmount > assetsCreated:
        contractsinfo[address].users[user].assetAmount += assetsCreated

    return


def handle_deposit_event(event):

    contractAddress = event["address"]
    depositer = event["args"]["depositer"]
    depositValue = event["args"]["depositValue"]
    endingValue = event["args"]["endingValue"]
    depositFeePaid = event["args"]["depositFeePaid"]
    ownerAddress = event["args"]["ownerAddress"]

    if depositer not in contractsinfo[address].users:
        return

    ##Check math and new values against event arguments
    if contractsinfo[address].users[depositer].etherAmount + depositValue - depositFeePaid < 0:
        return

    if contractsinfo[address].users[depositer].etherAmount + depositValue - depositFeePaid != endingValue:
        return

    ##Update balance
    contractsinfo[address].users[depositer].etherAmount += depositValue
    contractsinfo[address].users[depositer].etherAmount -= depositFeePaid

    ##Update etherassets
    contractsinfo[address].users[depositer].assetAmount += depositValue
    contractsinfo[address].users[depositer].assetAmount -= depositFeePaid

    ##Update owner account balance with deposit fee added
    contractsinfo[address].owner[ownerAddress].etherAmount += depositFeePaid


    ####Create depositValue - depositFeePaid worth of assets in Topl contract for user here####


    # for k,v in contractsinfo[address].users.items():
    #     print(k)
    #     print(v.toplAddress, v.etherAmount, v.assetAmount)
    # print()
    # print()
    print("worked")


def handle_start_withdrawal_event(event):

    contractAddress = event["address"]
    withdrawer = event["args"]["withdrawer"]
    withdrawalAmount = event["args"]["withdrawalAmount"]
    endingValue = event["args"]["endingValue"]
    withdrawalFee = event["args"]["withdrawalFee"]

    ##If the withdrawer has a pending withdrawal then deny the withdrawal

    if withdrawer in contractsinfo[address].inProgressWithdrawal:
        return

    ##If the withdrawal amount is less than minWithdrawalAmount for that contract then deny withdrawal
    if withdrawalAmount < contractsinfo[address].minWithdrawalAmount:
        return

    ## If the withdrawer does not have enough ether to cover the withdrawalAmount and withdrawal fee then deny withdrawal
    if contractsinfo[address].users[withdrawer].etherAmount - withdrawalAmount - withdrawalFee < 0:
        return

    # ## If the withdrawer does not have enough ether assets to cover the withdrawalAmount and withdrawal fee then deny withdrawal
    # if contractsinfo[address].users[withdrawer].assetAmount - withdrawalAmount - withdrawalFee < 0:
    #     return

    ##Check that there are enough ether assets on Topl side for this withdrawal##


    ##Create InProgressWithdrawal object for that user in the respective contract
    contractsinfo[address].inProgressWithdrawal[withdrawer] = InProgressWithdrawal(withdrawer, withdrawalAmount, endingValue, withdrawalFee)


    #print(event)
    return

def handle_approve_withdrawal_event(event):

    contractAddress = event["address"]
    withdrawer = event["args"]["withdrawer"]
    withdrawalAmount = event["args"]["withdrawalAmount"]
    endingValue = event["args"]["endingValue"]
    withdrawalFeePaid = event["args"]["withdrawalFeePaid"]
    ownerAddress = event["args"]["ownerAddress"]

    assert ownerAddress in contractsinfo[address].owner

    ##Check that the inProgressWithdrawal dictionary contains a request for withdrawal from the withdrawer
    if withdrawer not in contractsinfo[address].inProgressWithdrawal:
        return

    ##Check that incoming event information matches information stored in inProgressWithdrawal dictionary

    if contractsinfo[address].inProgressWithdrawal[withdrawer].withdrawalAmount != withdrawalAmount:
        return

    if contractsinfo[address].inProgressWithdrawal[withdrawer].withdrawalFee != withdrawalFeePaid:
        return

    if contractsinfo[address].inProgressWithdrawal[withdrawer].endingValue != endingValue:
        return

    ##Check math
    if contractsinfo[address].users[withdrawer].etherAmount - withdrawalAmount - withdrawalFeePaid != endingValue:
        return

    ##Make necessary changes to user etherAmount
    contractsinfo[address].users[withdrawer].etherAmount -= withdrawalAmount
    contractsinfo[address].users[withdrawer].etherAmount -= withdrawalFeePaid

    # ##Make necessary changes to users assetAmount
    contractsinfo[address].users[withdrawer].assetAmount -= withdrawalAmount
    contractsinfo[address].users[withdrawer].assetAmount -= withdrawalFeePaid

    ##Update owner account balance with withdrawal fee added
    contractsinfo[address].owner[ownerAddress].etherAmount += withdrawalFeePaid
    # contractsinfo[address].owner[ownerAddress].assetAmount += withdrawalFeePaid



    ###Destroy equivalent asset amount on Topl side##


    ##Delete inProgressWithdrawal object from that contract for that user
    del contractsinfo[address].inProgressWithdrawal[withdrawer]

    #print(event)
    return

def handle_deny_withdrawal_event(event):

    contractAddress = event["address"]
    withdrawer = event["args"]["withdrawer"]
    withdrawalAmount = event["args"]["withdrawalAmount"]
    ownerAddress = event["args"]["ownerAddress"]

    assert ownerAddress in contractsinfo[address].owner

    if withdrawer not in contractsinfo[address].inProgressWithdrawal:
        return

    if contractsinfo[address].inProgressWithdrawal[withdrawer].withdrawalAmount != withdrawalAmount:
        return

    del contractsinfo[address].inProgressWithdrawal[withdrawer]

    #print(event)
    return

##Change contractsinfo address to contractaddress variable for all below functions
def handle_set_deposit_fee_event(event):
    contractAddress = event["address"]
    ownerAddress = event["args"]["ownerAddress"]
    assert ownerAddress in contractsinfo[address].owner

    ##Check old fee
    if contractsinfo[address].depositFee != event["args"]["oldFee"]:
        return

    contractsinfo[address].depositFee = event["args"]["newFee"]


    #print ("DepositFee=",contractsinfo[address].depositFee)
    print("worked")
    return

def handle_set_withdrawal_fee_event(event):
    contractAddress = event["address"]
    ownerAddress = event["args"]["ownerAddress"]
    assert ownerAddress in contractsinfo[address].owner

    # print(event)

    ##Check old fee
    if contractsinfo[address].withdrawalFee != event["args"]["oldFee"]:
        return

    contractsinfo[address].withdrawalFee = event["args"]["newFee"]

    #print ("WithdrawalFee=",contractsinfo[address].withdrawalFee)
    print("worked")
    return

def handle_min_withdrawal_amount_event(event):
    contractAddress = event["address"]
    ownerAddress = event["args"]["ownerAddress"]
    assert ownerAddress in contractsinfo[address].owner

    ##Check old minWithdrawalAmount
    if contractsinfo[address].minWithdrawalAmount != event["args"]["oldAmount"]:
        return

    contractsinfo[address].minWithdrawalAmount = event["args"]["newAmount"]

    #print ("WithdrawalAmount=",contractsinfo[address].minWithdrawalAmount)
    print("worked")
    return

def handle_change_topl_address_event(event):
    contractAddress = event["address"]
    ethAddress = event["args"]["ethAdrs"]
    oldAddress = event["args"]["oldToplAdrs"]
    newAddress = event["args"]["newToplAdrs"]

    if contractsinfo[address].users[ethAddress].toplAddress != oldAddress:
        return

    contractsinfo[address].users[ethAddress].toplAddress = newAddress

    # for k,v in contractsinfo[address].users.items():
    #     print(k)
    #     print(v.toplAddress, v.etherAmount, v.assetAmount)
    # print()
    # print()
    print("worked")

    return

def handle_change_ethereum_address_event(event):
    contractAddress = event["address"]
    toplAddress = event["args"]["toplAdrs"]
    oldAddress = event["args"]["oldEthAdrs"]
    newAddress = event["args"]["newEthAdrs"]

    if oldAddress not in contractsinfo[address].users:
        return

    if contractsinfo[address].users[oldAddress].toplAdrs != toplAddress:
        return

    user = contractsinfo[address].users[oldAddress]
    del contractsinfo[address].users[oldAddress]
    contractsinfo[address].users[newAddress] = user

    # for k,v in contractsinfo[address].users.items():
    #     print(k)
    #     print(v.toplAddress, v.etherAmount, v.assetAmount)
    # print()
    # print()
    print("worked")

    return

def create_log_file():
    with open("log.txt", "w") as f:
        f.close()

def log(event):
    with open("log.txt", "a") as f:
        f.write(str(dict(event)))
        f.close()


###Catching event loops

async def deposit_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_deposit_event(event)
            log(event)
        await asyncio.sleep(poll_interval)


async def withdrawal_loop(start_withdrawal_event_filter, approve_withdrawal_event_filter, deny_withdrawal_event_filter, poll_interval):

    while True:
        for event in start_withdrawal_event_filter.get_new_entries():
            handle_start_withdrawal_event(event)
            log(event)
        for event in approve_withdrawal_event_filter.get_new_entries():
            handle_approve_withdrawal_event(event)
            log(event)
        for event in deny_withdrawal_event_filter.get_new_entries():
            handle_deny_withdrawal_event(event)
            log(event)
        await asyncio.sleep(poll_interval)


async def set_fee_loop(set_deposit_fee_event_filter, set_withdrawal_fee_event_filter, set_min_withdrawal_event_filter, poll_interval):

    while True:
        for event in set_deposit_fee_event_filter.get_new_entries():
            handle_set_deposit_fee_event(event)
            log(event)
        for event in set_withdrawal_fee_event_filter.get_new_entries():
            handle_set_withdrawal_fee_event(event)
            log(event)
        for event in set_min_withdrawal_event_filter.get_new_entries():
            handle_min_withdrawal_amount_event(event)
            log(event)
        await asyncio.sleep(poll_interval)


async def change_address_loop(topl_address_event_filter, ethereum_address_event_filter, poll_interval):

    while True:
        for event in ethereum_address_event_filter.get_new_entries():
            handle_change_ethereum_address_event(event)
            log(event)
        for event in topl_address_event_filter.get_new_entries():
            handle_change_topl_address_event(event)
            log(event)
        await asyncio.sleep(poll_interval)



def main():
    #web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

    print("Is Connected? ", web3.isConnected())
    print()
    accounts = web3.eth.accounts
    web3.eth.defaultAccount = accounts[0]

    create_log_file()
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    ##Listening for events
    # block_filter = web3.eth.filter('pending')
    # tx_filter = web3.eth.filter('latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                #log_loop(block_filter, 2),#number represents poll_interval
                #log_loop(tx_filter, 0.01),
                deposit_loop(contract.eventFilter("deposit_event"), 0.1),
                withdrawal_loop(contract.eventFilter("startedWithdrawal_event"),
                    contract.eventFilter("approvedWithdrawal_event"),
                    contract.eventFilter("deniedWithdrawal_event"), 0.1),
                set_fee_loop(contract.eventFilter("depositFeeSet_event"),
                    contract.eventFilter("withdrawalFeeSet_event"),
                    contract.eventFilter("minWithdrawalAmountSet_event"), 0.1),
                change_address_loop(contract.eventFilter("changedToplAddress_event"),
                    contract.eventFilter("changedEthAddress_event"), 0.1)))
    finally:
        loop.close()



if __name__ == '__main__':
    main()
