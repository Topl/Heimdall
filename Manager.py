from web3 import Web3, HTTPProvider
import json, time, asyncio

Path_Truffle = '/Users/yamirtainwala/Desktop/HeimdallManager/'
truffle_file = json.load(open(Path_Truffle + 'build/contracts/Heimdall.json'))
abi = truffle_file['abi']
bytecode = truffle_file['bytecode']


#contract_address = "0x173443c07291a6fe1c0ea7606df3f7d36ed4b310"

# class ContractManager:
#     def __init__(self):
#         self.web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

address = ""

class Contract:
    def __init__(self, ethaddress, topladdress, usersdict, owner, assetclass, depositfee, withdrawalfee, minwithdrawalamount, inProgressWithdrawal):
        self.users = usersdict
        self.owner = owner
        self.asset = assetclass
        self.depositfee = depositfee
        self.withdrawalfee = withdrawalfee
        self.minwithdrawalamount = minwithdrawalamount
        self.ethaddress = ethaddress
        self.topladdress = topladdress
        self.inProgressWithdrawal = {}


###Include in contract object
assets_per_ether = 0
# min_withdrawal_amount = 0
# deposit_fee = 0
# withdrawal_fee = 0

def set_eth_to_asset_rate(rate):
    assets_per_ether = rate


class Asset:
    def __init__(self, assetcode, conversionrate, assetamount):
        self.assetcode = assetcode
        self.assets_per_ether = assets_per_ether
        self.assetamount = assetamount


class User:
    def __init__(self, toplAddress, etheramount, assetamount):
        self.toplAddress = toplAddress
        self.etheramount = etheramount
        self.assetamount = assetamount

useraddress = "abc"
amount = 0



class InProgressWithdrawal:
    def __init__(self, ethaddress, withdrawalamount, endingvalue, withdrawalfeepaid, validwithdrawal):
        self.ethaddress = ethaddress
        self.withdrawalamount = withdrawalamount
        self.endingvalue = endingvalue
        self.withdrawalfeepaid = withdrawalfeepaid
        self.validwithdrawal = validwithdrawal



#usersInfo = {}
ownerAddress = "123"
ownerToplAddress = "123"
owneraccount = {ownerAddress: User(ownerToplAddress, 10000, 0)}

###Mapping of contract address to contract object
contractsinfo = {address: Contract(address, "", {}, owneraccount, None, 0, 0, 0)}


def add_user(useraddress, usertopladdress, assetamount, etheramount, contractaddress):
    contractsinfo[contractaddress].users["useraddress"] = User(usertopladdress, etheramount, assetamount)



##Handling event loops


def handle_deposit_event(event):
    # if(isinstance(event,bytes)):
    #     print(event.hex())
    # else:
    contractaddress = event["address"]
    depositer = event["args"]["depositer"]
    depositValue = event["args"]["depositValue"]
    endingValue = event["args"]["endingValue"]
    depositFeePaid = event["args"]["depositFeePaid"]
    print(event)
    print()


    ##Add user to database if they dont exist else update their balance
    if depositer in contractsinfo[address].users:
        assert contractsinfo[address].users[depositer].etheramount + depositValue - depositFeePaid >= 0
        contractsinfo[address].users[depositer].etheramount += depositValue
        contractsinfo[address].users[depositer].etheramount -= depositFeePaid
    else:
        ###Remove this - Topl accounts should not be created by Manager - only for testing###
        contractsinfo[address].users[depositer] = User("abc", endingValue, 0)

    ##Check math
    assert contractsinfo[address].users[depositer].etheramount == endingValue

    ##Update owner account balance with deposit fee added
    owneraccount[ownerAddress].etheramount += depositFeePaid


    ####Create depositValue - depositFeePaid worth of assets in Topl contract for user here####


    for k,v in contractsinfo[address].users.items():
        print(k)
        print(v.toplAddress, v.etheramount)
    print()
    print()



def handle_start_withdrawal_event(event):
    flag = 1
    ###Check if withdrawal amount is greater than min withdrawal
    ###Check if user has equivalent amount of asset
    ###Wait for approve Withdrawal event
    contractaddress = event["address"]
    withdrawer = event["args"]["withdrawer"]
    withdrawalAmount = event["args"]["withdrawalAmount"]
    endingValue = event["args"]["endingValue"]
    withdrawalFeePaid = event["args"]["withdrawalFeePaid"]

    ##If the withdrawer has a pending withdrawal then deny the withdrawal
    if withdrawer in contractsinfo[address].inProgressWithdrawal:
        flag = 0

    ##If the withdrawal amount is less than minWithdrawalAmount for that contract then deny withdrawal
    if withdrawalAmount < contractsinfo[address].minwithdrawalamount
        flag = 0

    ## If the withdrawer does not have enough ether to cover the withdrawalAmount and withdrawal fee then deny withdrawal
    if contractsinfo[address].users[withdrawer].etheramount - withdrawalAmount - withdrawalFeePaid < 0
        flag = 0

    ##Create InProgressWithdrawal object for that user in the respective contract
    contractsinfo[address].inProgressWithdrawal[withdrawer] = InProgressWithdrawal(withdrawer, withdrawalAmount, endingValue, withdrawalFeePaid, flag)



    print(event)
    return

def handle_approve_withdrawal_event(event):
    contractaddress = event["address"]

    contractaddress = event["address"]
    withdrawer = event["args"]["withdrawer"]
    withdrawalAmount = event["args"]["withdrawalAmount"]
    endingValue = event["args"]["endingValue"]
    withdrawalFeePaid = event["args"]["withdrawalFeePaid"]

    ##Check that incoming event information matches information stored in inProgressWithdrawal dictionary

    assert contractsinfo[address].inProgressWithdrawal[withdrawer].withdrawalamount == withdrawalAmount

    assert contractsinfo[address].inProgressWithdrawal[withdrawer].withdrawalfeepaid == withdrawalFeePaid

    assert contractsinfo[address].inProgressWithdrawal[withdrawer].endingvalue == endingValue

    ##Check that the withdrawal has been validated by Manager

    assert contractsinfo[address].inProgressWithdrawal[withdrawer].validwithdrawal == 1

    ##Make necessary changes to users dictionary for that contract
    contractsinfo[address].users[withdrawer].etheramount -= withdrawalAmount
    contractsinfo[address].users[withdrawer].etheramount -= withdrawalFeePaid

    ##Check that the updated usersdictionary matches event information
    assert contractsinfo[address].users[withdrawer].etheramount = endingValue


    ###Destroy equivalent asset amount 

    ##Delete inProgressWithdrawal object from that contract for that user
    del contractsinfo[address].inProgressWithdrawal[withdrawer]



    print(event)
    return

def handle_deny_withdrawal_event(event):
    contractaddress = event["address"]
    print(event)
    return

##Change contractsinfo address to contractaddress variable for all below functions
def handle_set_deposit_fee_event(event):
    contractaddress = event["address"]
    contractsinfo[address].depositfee = event["args"]["newFee"]
    return

def handle_set_withdrawal_fee_event(event):
    contractaddress = event["address"]
    contractsinfo[address].withdrawalfee = event["args"]["newFee"]
    return

def handle_min_withdrawal_amount_event(event):
    contractaddress = event["address"]
    contractsinfo[address].minwithdrawalamount = event["args"]["newAmount"]
    return

def handle_change_topl_address_event(event):
    contractaddress = event["address"]
    return

def handle_change_ethereum_address_event(event):
    contractaddress = event["address"]
    return


###Catching event loops

async def catch_deposit_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_deposit_event(event)
        await asyncio.sleep(poll_interval)


async def catch_start_withdrawal_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_start_withdrawal_event(event)
        await asyncio.sleep(poll_interval)

async def catch_approved_withdrawal_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_approve_withdrawal_event(event)
        await asyncio.sleep(poll_interval)

async def catch_denied_withdrawal_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_deny_withdrawal_event(event)
        await asyncio.sleep(poll_interval)

async def catch_set_deposit_fee_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_set_deposit_fee_event(event)
        await asyncio.sleep(poll_interval)

async def catch_set_withdrawal_fee_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_set_withdrawal_fee_event(event)
        await asyncio.sleep(poll_interval)

async def catch_min_withdrawal_amount_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_min_withdrawal_amount_event(event)
        await asyncio.sleep(poll_interval)


async def catch_change_topl_address_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_change_topl_address_event(event)
        await asyncio.sleep(poll_interval)

async def catch_change_ethereum_address_loop(event_filter, poll_interval):

    while True:
        for event in event_filter.get_new_entries():
            handle_change_ethereum_address_event(event)
        await asyncio.sleep(poll_interval)

# async def log_loop(event_filter, poll_interval):
#
#     while True:
#         for event in event_filter.get_new_entries():
#             print("Log:")
#             print(event)
#         await asyncio.sleep(poll_interval)



def main():
    web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

    print("Is Connected? ", web3.isConnected())
    print()
    accounts = web3.eth.accounts
    web3.eth.defaultAccount = accounts[0]
    #print(web3.eth.defaultAccount)

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    #print(contract)


    ##Listening for events
    block_filter = web3.eth.filter('pending')
    tx_filter = web3.eth.filter('latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                #log_loop(block_filter, 2),#number represents poll_interval
                #log_loop(tx_filter, 0.01),
                catch_deposit_loop(contract.eventFilter("deposit_event"), 0.01),
                catch_start_withdrawal_loop(contract.eventFilter("startedWithdrawal_event"), 0.01),
                catch_approved_withdrawal_loop(contract.eventFilter("approvedWithdrawal_event"), 0.01),
                catch_denied_withdrawal_loop(contract.eventFilter("deniedWithdrawal_event"), 0.01),
                catch_set_deposit_fee_loop(contract.eventFilter("depositFeeSet_event"), 0.01),
                catch_set_withdrawal_fee_loop(contract.eventFilter("withdrawalFeeSet_event"), 0.01),
                catch_min_withdrawal_amount_loop(contract.eventFilter("minWithdrawalAmountSet_event"), 0.01),
                catch_change_topl_address_loop(contract.eventFilter("changedToplAddress_event"), 0.01),
                catch_change_ethereum_address_loop(contract.eventFilter("changedEthAddress_event"), 0.01)))
    finally:
        loop.close()





if __name__ == '__main__':
    main()
