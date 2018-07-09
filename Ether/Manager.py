from web3.auto import w3
from SolcFunctions import *
from ast import literal_eval
from LogFunctions import *
import time

state_vars = {
    "contract_open": False,
    "owner_balance": 0,
    "withdrawal_fee": 0,
    "deposit_fee": 0,
    "owner_address": "0x0",
    "wei_balance": 0
}


def tx_deny_withdrawal(withdrawer_address, amount, withdrawal_fee, contract):
    contract.functions.denyWithdrawal(withdrawer_address, amount, withdrawal_fee).transact()


def tx_approve_withdrawal(withdrawer_address, amount, withdrawal_fee, contract):
    contract.functions.approveWithdrawal(withdrawer_address, amount, withdrawal_fee).transact()


def tx_toggle_contract_open(contract):
    contract.functions.toggleContractOpen().transact()


def write_log_line(line):
    with open("log.txt", "a") as f:
        f.write(line + "\n")


def handle_toggle_contract_open_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "old": bool(int(data[66:][:64].encode("utf-8"))),
        "new": bool(int(data[130:][:64].encode("utf-8")))
    }
    write_log_line("toggle_contract_open | " + str(fields))
    state_vars["contract_open"] = True
    state_vars["owner_address"] = fields["ownerAddress"]
    return fields


def handle_deposit_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "depositerAddress": data[66:][:64],
        "deposit": int(data[130:][:64].encode("utf-8"), 16),
        "depositFee": int(data[194:][:64].encode("utf-8"), 16),
        "toplAdrs": int(data[258:][:64].encode("utf-8"), 16)
    }
    write_log_line("deposit_event | " + str(fields))
    state_vars["owner_balance"] += fields["depositFee"]
    state_vars["wei_balance"] += fields["deposit"]
    state_vars["owner_address"] = fields["ownerAddress"]
    print("EMIT ASSET CREATION TRANSACTION FOR", fields["deposit"] - fields["depositFee"], "WEI TO", fields["toplAdrs"])
    return fields


def handle_start_withdrawal_event(data, contract, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "withdrawerAddress": data[66:][:64],
        "amount": int(data[130:][:64].encode("utf-8"), 16),
        "withdrawalFee": int(data[194:][:64].encode("utf-8"), 16)
    }
    write_log_line("start_withdrawal_event | " + str(fields))
    state_vars["owner_address"] = fields["ownerAddress"]
    print("CHECK IF", fields["amount"], "WEI ASSETS HAVE BEEN BURNED IN THE NAME OF", fields["withdrawerAddress"])
    if state_vars["burned_wei"][fields["withdrawerAddress"]] >= fields["amount"]:
        tx_approve_withdrawal(fields["withdrawerAddress"], fields["amount"], fields["withdrawalFee"], contract)
    else:
        tx_deny_withdrawal(fields["withdrawerAddress"], fields["amount"], fields["withdrawalFee"], contract)
    return fields


def handle_approve_withdrawal_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "withdrawerAddress": data[66:][:64],
        "amount": int(data[130:][:64].encode("utf-8"), 16),
        "withdrawalFee": int(data[194:][:64].encode("utf-8"), 16)
    }
    write_log_line("approve_withdrawal_event | " + str(fields))
    # this means transfer has succeeded so decrease the burned wei value and give ourselves the fee
    state_vars["burned_wei"][fields["withdrawerAddress"]] -= fields["amount"]
    state_vars["owner_balance"] += fields["withdrawalFee"]
    state_vars["owner_address"] = fields["ownerAddress"]
    return fields


def handle_deny_withdrawal_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "withdrawerAddress": data[66:][:64],
        "amount": int(data[130:][:64].encode("utf-8"), 16),
        "withdrawalFee": int(data[194:][:64].encode("utf-8"), 16)
    }
    write_log_line("deny_withdrawal_event | " + str(fields))
    state_vars["owner_address"] = fields["ownerAddress"]
    return fields


def handle_set_deposit_fee_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "old": data[66:][:64],
        "new": data[130:][:64]
    }
    write_log_line("set_deposit_fee_event | " + str(fields))
    state_vars["deposit_fee"] = fields["new"]
    state_vars["owner_address"] = fields["ownerAddress"]
    return fields


def handle_set_withdrawal_fee_event(data, state_vars):
    fields = {
        "ownerAddress": data[2:][:64],
        "old": data[66:][:64],
        "new": data[130:][:64]
    }
    write_log_line("set_withdrawal_fee_event | " + str(fields))
    state_vars["withdrawal_fee"] = fields["new"]
    state_vars["owner_address"] = fields["ownerAddress"]
    return fields


def main():
    abi = abi_heimdall()
    bytecode = bytecode_heimdall()
    print("connected:", w3.isConnected())
    print("loading...")
    accounts = w3.eth.accounts
    w3.eth.defaultAccount = accounts[0]
    heimdall_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    with open("log.txt", "r") as f:
        if f.read() == "new deploy":
            tx_hash_heimdall_deployment = heimdall_contract.constructor().transact()
            tx_receipt_heimdall_deployment = w3.eth.waitForTransactionReceipt(tx_hash_heimdall_deployment)
            heimdall_contract_address = tx_receipt_heimdall_deployment.contractAddress
            with open("log.txt", "w") as fw:
                fw.write(heimdall_contract_address + "\n")
        else:
            f.seek(0)
            heimdall_contract_address = f.read(42)
            # load log data
            f.seek(0)
            for line in f.readlines()[1:]:
                clean_line = line.strip("\n")
                line_parts = line.split(" | ")
                line_parts[1] = literal_eval(line_parts[1])
                handle_log_line(line_parts, state_vars)
    print("deployment account:", w3.eth.defaultAccount)
    print("contract deployed to:", heimdall_contract_address)
    heimdall_contract = w3.eth.contract(
        address=heimdall_contract_address,
        abi=abi,
        bytecode=bytecode
    )
    # create event filters
    toggle_contract_open_event_hash = w3.sha3(text="ToggleContractOpenEvent(address,bool,bool)").hex()
    toggle_contract_open_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [toggle_contract_open_event_hash]
    })
    deposit_event_hash = w3.sha3(text="DepositEvent(address,address,uint256,uint256,uint256)").hex()
    deposit_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [deposit_event_hash]
    })
    start_withdrawal_event_hash = w3.sha3(text="StartWithdrawalEvent(address,address,uint256,uint256)").hex()
    start_withdrawal_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [start_withdrawal_event_hash]
    })
    approve_withdrawal_event_hash = w3.sha3(text="ApproveWithdrawalEvent(address,address,uint256,uint256)").hex()
    approve_withdrawal_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [approve_withdrawal_event_hash]
    })
    deny_withdrawal_event_hash = w3.sha3(text="DenyWithdrawalEvent(address,address,uint256,uint256)").hex()
    deny_withdrawal_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [deny_withdrawal_event_hash]
    })
    set_deposit_fee_event_hash = w3.sha3(text="SetDepositFeeEvent(address,uint256,uint256)").hex()
    set_deposit_fee_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [set_deposit_fee_event_hash]
    })
    set_withdrawal_fee_event_hash = w3.sha3(text="SetWithdrawalFeeEvent(address,uint256,uint256)").hex()
    set_withdrawal_fee_event_filter = w3.eth.filter(filter_params={
        "address": heimdall_contract_address,
        "topics": [set_withdrawal_fee_event_hash]
    })
    try:
        while True:
            print("\t--")
            heimdall_contract.functions.toggleContractOpen().transact()
            heimdall_contract.functions.setWithdrawalFee(50).transact()

            for event in toggle_contract_open_event_filter.get_new_entries():
                handle_toggle_contract_open_event(event["data"], state_vars)
                print("toggled", event)
            for event in deposit_event_filter.get_new_entries():
                handle_deposit_event(event["data"], state_vars)
            for event in start_withdrawal_event_filter.get_new_entries():
                handle_start_withdrawal_event(event["data"], heimdall_contract, state_vars)
            for event in approve_withdrawal_event_filter.get_new_entries():
                handle_approve_withdrawal_event(event["data"], state_vars)
            for event in deny_withdrawal_event_filter.get_new_entries():
                handle_deny_withdrawal_event(event["data"], state_vars)
            for event in set_deposit_fee_event_filter.get_new_entries():
                handle_set_deposit_fee_event(event["data"], state_vars)
            for event in set_withdrawal_fee_event_filter.get_new_entries():
                handle_set_withdrawal_fee_event(event["data"], state_vars)
            # update topl data
            time.sleep(2)
    except:
        if state_vars["contract_open"]:
            tx_toggle_contract_open(heimdall_contract)


if __name__ == '__main__':
    main()
