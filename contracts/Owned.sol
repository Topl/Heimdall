pragma solidity ^0.4.0;

contract Owned {

    address owner;

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function newOwner(address _newOwner) onlyOwner public {
        owner = _newOwner;
    }
}
