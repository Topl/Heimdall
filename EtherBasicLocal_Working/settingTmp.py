import abi
import requests
import sys
import time
from jsonrpcclient.clients.http_client import HTTPClient
import logging
from web3 import Web3
from web3 import Account
from web3.middleware import geth_poa_middleware
contract_address = "0x49e80425fb0696c642bd840e87a8aac0847f65a7"
manager_ethereum_public_key = "0x5B12A6a70300B5A0734742845aC4f5a366f7997C"
manager_ethereum_private_key = "1610002447a325188582c4e366892ecc200cef4dec7a37190807b1544e425dc5"
manager_topl_public_key = "6sYyiTguyQ455w2dGEaNbrwkAWAEYV1Zk6FtZMknWDKQ"
manager_topl_public_key_password = "genesis"
black_hole_address = "22222222222222222222222222222222222222222222"
w3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
#w3.middleware_stack.inject(geth_poa_middleware, layer=0)
w3.eth.defaultAccount = Account.privateKeyToAccount(manager_ethereum_private_key)
start_block = 2500000  # can move this up if you are starting far in the future
contract = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi.ContractABI)
t_event = contract.events.t.createFilter(fromBlock=1)
g_event = contract.events.g.createFilter(fromBlock=1)
##requests.post("http://localhost:9085/wallet/unlock",
##              headers={"Accept": "application/json", "Content-Type": "application/json"},
##              json={"password": manager_topl_public_key_password,
##                    "publicKey": manager_topl_public_key}).json()
