var MyContract = artifacts.require("send_me_money");

module.exports = function(deployer, network, accounts) {
    deployer.deploy(MyContract, {from: accounts[0]}).then(function() {
        console.log("\n\n\n\n");
        console.log("THESE ARE THE ADDRESSES YOU NEED");
        console.log("-------------------------------------------------------------------------------------");
        console.log("THE ADDRESS THE CONTRACT WAS DEPLOYED AT: ", MyContract.address);
        console.log("-------------------------------------------------------------------------------------");
        console.log("\n\n\n\n");
    })
};