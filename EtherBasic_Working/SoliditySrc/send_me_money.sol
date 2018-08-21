pragma solidity 0.4.24;

contract send_me_money {
    address owner;

    constructor() public {
        owner = msg.sender;
    }

    function take(uint256 _v) public payable {
        emit t(msg.sender, msg.value, _v);
    }

    function give(address _a, uint256 _v) public {
        assert(msg.sender == owner);
        _a.transfer(_v);
        emit g(_a, _v);
    }

    function new_owner(address _a) public {
        assert(msg.sender == owner);
        owner = _a;
    }

    event t(address sender, uint256 amount, uint256 receiver);
    event g(address receiver, uint256 amount);
}

