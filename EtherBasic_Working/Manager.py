from EtherBasic_Working import abi
import requests
import time
from jsonrpcclient.http_client import HTTPClient
import logging
from web3 import Web3
from web3 import Account
from web3.middleware import geth_poa_middleware

logging.disable(logging.CRITICAL)


def base_n(num, b, numerals="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def space_pad(target, cur):
    r = ""
    for i in range(target - cur):
        r += " "
    return r


def main():
    # USER INPUT
    print("\nPlease enter the full path to your Geth node's IPC file.")
    print("Note that the IPC file you choose determines the chain on which your Heimdallr instance will be deployed.\n")
    ipc_path = input("IPC FILE PATH: ")
    if ipc_path != "TEST":
        print("Please enter your Etherscan.io API key.")
        print("Note that this key doesn't give this program any control over any of your (or anyone else's funds).\n")
        etherscan_key = input("ETHERSCAN API KEY: ")
        print("\nCurrently this program assumes your Heimdallr contract is already deployed.")
        print("This is planned to change in a future update adding a SmartDeploy feature.")
        print("The exact source code of the contract you are expected to have deployed can be found here:"
              " https://github.com/Topl/Heimdallr/blob/master/EtherBasic_Working/SoliditySrc/send_me_money.sol")
        print("Unless you'd like to wait till then, please enter the address of your ALREADY DEPLOYED contract.\n")
        contract_address = input("CONTRACT ADDRESS: ")
        print("\nPlease enter the public key of the Ethereum account you'd like to use.")
        print("Note that this public key must be the 'owner' of the contract you deployed.\n")
        manager_ethereum_public_key = input("ETHEREUM PUBLIC KEY: ")
        print("\nPlease enter the private key of the public key you just entered.")
        print("This private key is never saved to a file but is stored in memory for the duration of this program's life.")
        print("Because of this, it is strongly recommended that you only run this program on a secure machine.\n")
        manager_ethereum_private_key = input("ETHEREUM PRIVATE KEY: ")
        print("\nPlease enter the Topl public key you'd like your Heimdallr instance to mint wei assets with.\n")
        manager_topl_public_key = input("TOPL PUBLIC KEY: ")
        print("\nPlease enter the password for the public key you previously entered.")
        print("Note that, unlike your Ethereum private key, this password will only be used to unlock your keyfile.")
        print("After this has happened it will be overwritten in memory to reduce the risk of theft.\n")
        manager_topl_public_key_password = input("TOPL KEYFILE PASSWORD: ")
        print("\nPlease enter youd desired black hole address.")
        print("This is the address people wanting to withdraw wei assets will send their wei to.")
        print("It can be made up of any of the following characters: "
              "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        print("It must be 44 characters long and can't be all 1s.\n")
        black_hole_address = input("BLACK HOLE ADDRESS: ")
        print("\nIs this an initial setup or are you restarting a Heimdallr instance"
              " that has already been used before?\n")
        new_instance = input("INSTANCE TYPE ('new' or 'old'): ")
    else:  # testing defaults
        #
        # NOT GOING
        # TO PUT
        # MY PRIVATE
        # KEY ON
        # GITHUB
        #
    if new_instance == 'new':
        new_instance = True
    else:
        new_instance = False
    print("\n\n\n")

    # WEB3 SETUP
    my_provider = Web3.IPCProvider(ipc_path)
    w3 = Web3(my_provider)
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    w3.eth.defaultAccount = Account.privateKeyToAccount(manager_ethereum_private_key)
    start_block = 2500000  # can move this up if you are starting far in the future

    # TOPL SETUP
    requests.post("http://localhost:9585/wallet/unlock",
                  headers={"Accept": "application/json", "Content-Type": "application/json"},
                  json={"password": manager_topl_public_key_password,
                        "publicKey": manager_topl_public_key}).json()
    client = HTTPClient("http://localhost:9585/asset/")

    # DEPLOY CONTRACT
    # in progress
    # - need to do actual deploy
    # - need to set contract address var
    # - need to make contract source code var in abi.py
    contract = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi.ContractABI)

    # HISTORICAL SETUP
    completed_deposits = []
    completed_withdrawals = []
    if not new_instance:
        topl_blocks = []
        with open("completed_deposits.txt", "r") as f:
            for line in f.readlines():
                completed_deposits.append(line.strip("\n"))
        with open("completed_withdrawals.txt", "r") as f:
            for line in f.readlines():
                completed_withdrawals.append(line.strip("\n"))
    else:
        topl_blocks = requests.get("http://localhost:9585/debug/chain").json()["data"]["history"].split(",")[::-1]

    # EVENT LOOP
    while True:
        etherscan_logs = requests.get("https://api-rinkeby.etherscan.io/api?module=logs&action=getLogs&fromBlock=" \
              + str(start_block) + "&toBlock=latest&address=" + contract_address + "&apikey=" \
              + etherscan_key).json()["result"]  # get etherscan logs
        print("EVENT      : SENDER                                    "
              " : RECIEVER                                     : VALUE")  # header text
        print("--------------------------------------------------------"
              "--------------------------------------------------------"
              "- --- -- - -  -  -   -    -     -")  # header line
        for resp in etherscan_logs:
            if resp["topics"] == ["0x760df8dd8f30d25b7060528c28184a2f51bfc376f198001e5e1cb17f8a4115f5"]:  # deposits
                print("deposit    :", "0x" + resp["data"][2:][24:64], ":",
                      base_n(int(resp["data"][2:][128:], 16), 58),
                      space_pad(44, len(base_n(int(resp["data"][2:][128:], 16), 58))) + ":",
                      int(resp["data"][2:][64:128], 16))  # raw log info (no address padding)
                start_block = int(resp["blockNumber"], 16) - 1  # update filter start block for next iteration
                if resp["transactionHash"] in completed_deposits:
                    print("PREVIOUSLY SEEN")
                else:
                    addr = base_n(int(resp["data"][2:][128:], 16), 58)
                    asset_amount = int(resp["data"][2:][64:128], 16)
                    if len(addr) > 44:
                        print("                         "
                              "                                 ^- INVALID TOPL ADDRESS")  # invalid topl address
                    elif asset_amount <= 0:
                        print("                                                            "
                              "                                   "
                              "          ^- INVALID ASSET AMOUNT")  # invalid asset amount
                    else:
                        if len(addr) < 44:
                            r = 44 - len(addr)
                            print(r)
                            for i in range(int(r/2)):
                                addr = "1" + addr  # pad for addresses with leading zeroes
                        print(addr)
                        asset_creation_resp = client.send('{"jsonrpc": "2.0", "id": "1", "me'
                                                   'thod": "createAssets", "params": [{"hub": "'
                                                   + manager_topl_public_key + '", "to": "'
                                                   + addr + '", "amount": ' + str(asset_amount)
                                                   + ', "assetCode": "wei", "fee": 0}]}')  # create assets
                        print("Assets Created", asset_creation_resp)
                    completed_deposits.append(resp["transactionHash"])
                    with open("completed_deposits.txt", "a") as f:
                        f.write(resp["transactionHash"] + "\n")
            else:  # withdrawals
                print("withdrawal : MANAGER                                    :",
                      "0x" + resp["data"][2:][24:64], "  :", int(resp["data"][2:][64:128], 16))  # raw log info
                start_block = int(resp["blockNumber"], 16) - 1  # update filter start block for next iteration
                if resp["transactionHash"] in completed_withdrawals:
                    print("PREVIOUSLY SEEN")
                else:
                    completed_withdrawals.append(resp["transactionHash"])
                    with open("completed_withdrawals.txt", "a") as f:
                        f.write(resp["transactionHash"] + "\n")
            print("")
        print("\n\n")
        block_ids = requests.get("http://localhost:9585/debug/chain").json()["data"]["history"].split(",")[::-1]
        for block_id in block_ids:
            if block_id not in topl_blocks:
                block_txs = \
                requests.get("http://localhost:9585/nodeView/persistentModifier/" + block_id).json()["data"]["txs"]
                for tx in block_txs:
                    if "assetCode" in tx and "hub" in tx:
                        if tx["assetCode"] == "wei" and tx["hub"] == manager_topl_public_key \
                                and tx["id"] not in completed_withdrawals:  # new, wei, and from me
                            for prop in tx["to"]:
                                if prop["proposition"] == black_hole_address:  # burn box
                                    print("Wei burned!")
                                    print(tx)
                                    nonce = w3.eth \
                                        .getTransactionCount(w3.toChecksumAddress(manager_topl_public_key_password))
                                    w3.eth.sendRawTransaction(w3.eth.account
                                                              .signTransaction(contract
                                                                               .functions
                                                                               .give(w3
                                                                                     .toChecksumAddress(tx["data"]),
                                                                                     int(prop["value"]))
                                                                               .buildTransaction({"chainId": 4,
                                                                                                  "gas": 100000,
                                                                                                  "gasPrice": w3
                                                                                                 .toWei('1',
                                                                                                        'gwei'),
                                                                                                  "nonce": nonce}),
                                                                               private_key=
                                                                               manager_ethereum_private_key)
                                                              .rawTransaction)  # send that SH*T
                                    completed_withdrawals.append(tx["id"])
                                    with open("completed_withdrawals.txt", "a") as f:
                                        f.write(tx["id"] + "\n")
                topl_blocks.append(block_id)
            else:
                break
        print("\n\n")

        time.sleep(10)


if __name__ == "__main__":
    main()
