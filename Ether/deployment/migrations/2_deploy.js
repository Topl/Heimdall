var Heimdall = artifacts.require("./Heimdall.sol");

module.exports = function(deployer, network, accounts) {
	deployer.deploy(Heimdall, {from: accounts[0]}).then(function(instance) {
		console.log(instance.address);
		console.log(accounts)
	});
};