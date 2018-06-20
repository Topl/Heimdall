pragma solidity 0.4.23;


contract Owned {

    address public owner;

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function terminate() external onlyOwner {
        selfdestruct(owner);
    }

    function newOwner(address _newOwner) public onlyOwner {
        owner = _newOwner;
    }
}
