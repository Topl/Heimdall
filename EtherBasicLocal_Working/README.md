# Heimdallr Ether Basic (Local)
Heimdallr Ether Basic is a simplistic implementation of Heimdallr Ether, a sidechaining service for use between the Ethereum and Topl. This directory contains Heimdallr Ether Basic (Local) which is a version of Heimdallr Ether Basic built to allow for experimental local testing. It uses a ganache-cli instance instead of a Geth node. It is, however, the same as Heimdallr Ether Basic (Public) in almost every other way.
## Setup
Heimdallr Ether Basic (Local) requires minimal user setup. The following is a step-by-step guide to the setup of a brand new Heimdallr Ether Basic (Local) instance.
1) Ensure you have Truffle and Ganache-CLI installed on your machine. If you don't, refer to this documentation (https://truffleframework.com/docs) to find out how to install both. If you're not sure wheather you have Truffle and Ganache-CLI installed run the following command: ```truffe & ganache-cli -?``` If you get a ``` command not found``` error you don't have the corresponding package installed and must install it before proceeding.
2) Additionally, this guide assumes you have the following version of python and the following pip modules. Installation of these, should you not have them already, is outside the scope of this guide, but can usually be found on the different modules' respective READMEs.
    * python version: 3.6.0
    * web3 version: 4.5.0
    * jsonrpcclient version: 2.6.0
3) Now that you have the required tools, let's get to the actual setup. Run ```ganache-cli```. This will start up your local Ganache blockchain on which we will deploy your test contract. In the print out that this creates is a list of 10 public keys as well as a list of 10 private keys. Note the first key in each of these lists. You'll need them for later.
5) Now, assuming you have the Bifrost private JAR (you can download it here if you don't https://github.com/Topl/Bifrost/releases), in a new terminal run ```java -jar project-bifrost-0.2.2-alpha-private.jar```.
4) In yet another new terminal cd to the Heimdallr directory this should look something like ```cd ~/Desktop/Heimdallr``` though it will vary depending on where you download this repo to. Next run ```cd EtherBasicLocal_Working/Deployment``` followed by ```truffle migrate --reset```. This will deploy your test contract to your Ganache blockchain. Note the address it says your contract was deployed at. You'll need it later.
6) Next, in the same terminal, run ```cd ..``` followed by ```python3 Mananager.py```. This will start your manager.
7) The manager will ask for a series of inputs that it needs to operate. When it asks for CONTRACT ADDRESS give it the address you noted in step 4. When it asks for ETHEREUM PUBLIC KEY give it the public key you noted in step 3. When it asks for ETHEREUM PRIVATE KEY give it the private key you noted in step 3. Then for TOPL PUBLIC KEY and TOPL KEYFILE PASSWORD use whatever key you've generated for yourself. This can be done via swagger (information can be found here https://github.com/Topl/Bifrost/wiki/HTTP-API). Finally, for BLACK HOLE ADDRESS give it 22222222222222222222222222222222222222222222.
8) That concludes setup. You can now interact with your Heimdallr Ether Basic (Local) instance.
## Interaction
So, you want to actually use your new sidechain? Well here's how.
### The console
All interaction with the Heimdallr Ether Basic smart contract will happen via the truffle console. To start it up, open a terminal and run ```truffle console --network development```.
This will bring up a REPL in which you can run web3.
### The contract
Before we can send money to our contract we need to create the contract object that we will interact with. This can be done with the following command:

```con = web3.eth.contract([ { "constant": false, "inputs": [ { "name": "_a", "type": "address" } ], "name": "new_owner", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "name": "_v", "type": "string" } ], "name": "take", "outputs": [], "payable": true, "stateMutability": "payable", "type": "function" }, { "constant": false, "inputs": [ { "name": "_a", "type": "address" }, { "name": "_v", "type": "uint256" } ], "name": "give", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "payable": false, "stateMutability": "nonpayable", "type": "constructor" }, { "anonymous": false, "inputs": [ { "indexed": false, "name": "sender", "type": "address" }, { "indexed": false, "name": "amount", "type": "uint256" }, { "indexed": false, "name": "receiver", "type": "string" } ], "name": "t", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": false, "name": "receiver", "type": "address" }, { "indexed": false, "name": "amount", "type": "uint256"} ], "name": "g", "type": "event"} ])```

Yeah, it's a big one. Now you just need to link this contract object to your contract on chain. To do this, run ```con.at(INSERT ADDRESS)```. Where it says INSERT ADDRESS put the address of your deployed contract in double-quotes instead. 
### Sending wei to Topl
To send wei to the take function of your contract (AKA send wei to the Topl blockchain) you can issue the following command:

```con.take(INSERT TOPL ADDRESS, {value: AMOUNT, gas: 100000})```

Where it say INSERT TOPL ADDRESS put your Topl address in double-quotes instead. Where it says AMOUNT put the amount of wei you'd like to send instead.
### Sending wei assets to Ethereum
IN PROGRESS