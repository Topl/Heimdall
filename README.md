# Sidechaining
## State
This project is not yet done, and should not be used in production. If it is used it will almost certainly have bugs, and it will almost certainly lose you money. 
## How To Use
This repo contains two smart contracts and a manager client. Combined these allow a user to connect the Ethereum and Topl blockchains together to allow for Ether Assets on the Topl blockchain. This is accomplished by first broadcasting the Ethereum and Topl smart contracts to their respective chains. Then configuring the manager client (more on this in the config section).

Assuming a complete and proper setup the Heimdall sidechaining implementation should allow one to lock up Ether for customers on the Ethereum blockchain and create Ether Assets on the Topl blockchain which are symbolicly backed by the customers' locked Ether. However, the Topl blockchain requires sidechaining entities (crypto asset creators) to have a certain amount of Arbits staked to be given the privilege of creating on-chain crypto-backed assets. Because of this all prospective users are urged to look up the costs associated with becoming a crypto asset creator before trying to setup a Heimdall sidechaining instance for themselves.
## The Model
Heimdall takes uses a partial trust model. This model allows customers of Heimdall instances to deposit and withdraw Ether from the Topl blockchain easily while have strong proof that it is impossible for a Heimdall instance owner to steal their locked Ether.

However, Heimdall does not use a fully trustless model. Customers of Heimdall instances still accept the risk that a Heimdall instance owner may, at its absolute discretion, freeze their funds at any point during the transfer from Ethereum to Topl or back. Additionally, the Heimdall instance owner has the ability to create Ether assets on the Topl blockchain without out regard for this protocol. This is not a problem with Heimdall so much as it is a problem with tokenized assets generation in general.

Heimdall justifies and mitigates these risks through a free-market. The idea being that any Topl blockchain user with enough Arbits can become a crypto asset creator (and therefore a Heimdall instance owner). This means that all sidechain instances are incentivized to give customers a good experience both in terms of fees and fraud.

This free-market approach will be further strengthened by open-source sidechaining managers that allow users to switch to whichever sidechain has the lowest fees and best reputation with little to no friction. Think of it like a universal bank account that allows it's owner to instantly and freely decide which bank's savings and checkings accounts to use based on interest, reputation, speed, and any other relevant factor.
## config
In Progress

## to do
- manager

