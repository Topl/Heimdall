from EtherBasicLocal_Working import abi
import requests
import sys
import time
from jsonrpcclient.http_client import HTTPClient
import logging
from web3 import Web3
from web3 import Account
from web3.middleware import geth_poa_middleware

logging.disable(logging.CRITICAL)


# def base_n(num, b, numerals=):
#     return ((num == 0) and numerals[0]) or (base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def base_n(num, alphabet="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def space_pad(target, cur):
    r = ""
    for i in range(target - cur):
        r += " "
    return r


def event_handler(event):
    if event["event"] == "t":
        return take_event_handler(event)
    elif event["event"] == "g":
        return give_event_handler(event)
    else:
        raise Exception("Unknown event" + str(event))


def take_event_handler(event):
    try:
        amount = str(event["args"]["amount"])
        receiver = event["args"]["receiver"]
        if int(amount) == 0:
            raise Exception("assertion failed: Invalid amount")
        s = '{"jsonrpc": "2.0", "id": "1", "method": "createAssets", "params": [{"hub": "' + manager_topl_public_key + '", "to": "' + receiver + '", "amount": ' + amount + ', "assetCode": "wei", "fee": 0}]}'
        r = client.send(s)
        print("Deposit Routed", r)
    except Exception as E:
        print(E)
        pass
    with open("completed_txs.txt", "a") as f:
        f.write(str(event["transactionHash"]) + "\n")
    return str(event["transactionHash"])


def give_event_handler(event):
    try:
        amount = str(event["args"]["amount"])
        receiver = event["args"]["receiver"]
        if int(amount) == 0:
            raise Exception("assertion failed: Invalid amount")
        print("Withdrawal Noted")
    except Exception as E:
        print(E)
        pass
    with open("completed_txs.txt", "a") as f:
        f.write(str(event["transactionHash"]) + "\n")
    return str(event["transactionHash"])


def main():
    # WEB3 SETUP
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    w3.eth.defaultAccount = Account.privateKeyToAccount(manager_ethereum_private_key)
    start_block = 2500000  # can move this up if you are starting far in the future

    # UNLOCK KEYFILE
    requests.post("http://localhost:9585/wallet/unlock",
                  headers={"Accept": "application/json", "Content-Type": "application/json"},
                  json={"password": manager_topl_public_key_password,
                        "publicKey": manager_topl_public_key}).json()

    # DEPLOY CONTRACT
    # in progress
    # - need to do actual deploy
    # - need to set contract address var
    # - need to make contract source code var in abi.py
    contract = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi.ContractABI)

    # LOGS SETUP
    t_event = contract.events.t.createFilter(fromBlock=2800000)
    g_event = contract.events.g.createFilter(fromBlock=2800000)

    # HISTORICAL SETUP
    tx_hashes = []
    if not new_instance:
        topl_blocks = []
        with open("completed_blocks.txt", "r") as f:
            for line in f.readlines():
                topl_blocks.append(line.strip("\n"))
        with open("completed_txs.txt", "r") as f:
            for line in f.readlines():
                tx_hashes.append(line.strip("\n"))
        all_events = t_event.get_all_entries() + g_event.get_all_entries()
        to_do_events = []
        for e in all_events:
            if e["transactionHash"] not in tx_hashes:
                to_do_events.append(e)
    else:
        to_do_events = []
        topl_blocks = requests.get("http://localhost:9085/debug/chain").json()["data"]["history"].split(",")[::-1]


    # EVENT LOOP
    while True:
        print("--------------------------------------------------------"
              "--------------------------------------------------------"
              "- --- -- - -  -  -   -    -     -")  # header line
        to_do_events += t_event.get_new_entries()  # get new events
        to_do_events += g_event.get_new_entries()  # get new events
        for e in to_do_events:
            print("event:", e)  # print out event
            tx_hashes.append(event_handler(e))  # handle each event
        block_ids = requests.get("http://localhost:9085/debug/chain").json()["data"]["history"].split(",")[::-1]
        for block_id in block_ids:
            if block_id not in topl_blocks:
                block_txs = requests.get("http://localhost:9085/nodeView/persistentModifier/" + block_id).json()["data"]["txs"]
                for tx in block_txs:
                    if tx.get("assetCode", "") == "wei" and tx.get("hub", "") == manager_topl_public_key and tx["id"] not in tx_hashes:  # new, wei, and from me
                        for prop in tx["to"]:
                            if prop["proposition"] == black_hole_address:  # burn box
                                print("Wei burned!")
                                print(tx)
                                nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(manager_topl_public_key_password))
                                w3.eth.sendRawTransaction(w3
                                                          .eth
                                                          .account
                                                          .signTransaction(contract
                                                                           .functions
                                                                           .give(w3.toChecksumAddress(tx["data"]), int(prop["value"]))
                                                                           .buildTransaction({"chainId": 4, "gas": 100000, "gasPrice": w3.toWei('5', 'gwei'), "nonce": nonce}),
                                                                           manager_ethereum_private_key)
                                                          .rawTransaction)  # send that SH*T
                                tx_hashes.append(tx["id"])
                                with open("completed_txs.txt", "a") as f:
                                    f.write(tx["id"] + "\n")
                topl_blocks.append(block_id)
                with open("completed_blocks.txt", "a") as f:
                    f.write(block_id + "\n")
            else:
                break
        to_do_events = []
        print("\n\n")
        time.sleep(5)


#
# START HERE
#

# GLOBAL SETUP
client = HTTPClient("http://localhost:9085/asset/")

# USER INPUT
print("\nDefaults must be set in the source code before this option can be chosen.")
print("If you haven't set defaults enter 'n'\n")
defaults = input(" RUN DEFAULTS ('y' or 'n'): ")
if defaults == "n":
    print("\nCurrently this program assumes your Heimdallr contract is already deployed.")
    print("This is planned to change in a future update adding a SmartDeploy feature.")
    print("The exact source code of the contract you are expected to have deployed can be found here:"
          " https://github.com/Topl/Heimdallr/blob/master/EtherBasicLocal_Working/SoliditySrc/send_me_money.sol")
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
    contract_address = "FILL HERE"
    manager_ethereum_public_key = "FILL HERE"
    manager_ethereum_private_key = "FILL HERE"
    manager_topl_public_key = "FILL HERE"
    manager_topl_public_key_password = "FILL HERE"
    black_hole_address = "FILL HERE"
    new_instance = 'FILL HERE'
if new_instance == 'new':
    new_instance = True
else:
    new_instance = False
print("\n\n\n")

# ENTER MAIN
main()
