pragma solidity ^0.4.23;

import "./SafeMath.sol";
import "./Owned.sol";

contract BifrostStorage is Owned{

    using SafeMath for uint256; // overflow checks

    /// contract vars
    address public currentMaster;

    /// structs
    struct user {
        string toplAdrs;
        uint256 balance;
    }

    /// storage vars
    mapping(address => user) public users;
    mapping(address => uint256) public inProgress;
    uint256 public minWithdrawalAmount;
    uint256 public withdrawalFee;
    uint256 public depositFee;

    /// constructor
    constructor() {
        currentMaster = 0x0;
    }

    /// master function & modifier (IE deciding which contract can use this storage)
    modifier fromMaster() {
        require(msg.sender == currentMaster);
        _;
    }

    function changeMaster(address _newMaster) onlyOwner public {
        currentMaster = _newMaster;
    }

    /// edit var functions
    function editVar_users(address _ethAdrs, string _toplAdrs, uint256 _balance) fromMaster public {
        users[_ethAdrs].toplAdrs = _toplAdrs;
        users[_ethAdrs].balance = _balance;
    }

    function editVar_inProgress(address _ethAdrs, uint256 _amount) fromMaster public {
        inProgress[_ethAdrs] = _amount;
    }

    function editVar_minWithdrawalAmount(uint256 _minWithdrawalAmount) fromMaster public {
        minWithdrawalAmount = _minWithdrawalAmount;
    }

    function editVar_withdrawalFee(uint256 _withdrawalFee) fromMaster public {
        withdrawalFee = _withdrawalFee;
    }

    function editVar_depositFee(uint256 _depositFee) fromMaster public {
        depositFee = _depositFee;
    }

    /// load var functions
    function loadVar_users_keyValue(address _ethAdrs) fromMaster view public {
        return (users[_ethAdrs].toplAdrs, users[_ethAdrs].balance); // returns a list because structs are just loose variable bags NOT objects
    }

    function loadVar_inProgress_keyValue(address _ethAdrs) fromMaster view public {
        return inProgress[_ethAdrs];
    }

    function loadVar_minWithdrawalAmount() fromMaster view public {
        return minWithdrawalAmount;
    }

    function loadVar_withdrawalFee() fromMaster view public {
        return withdrawalFee;
    }

    function loadVar_depositFee() fromMaster view public {
        return depositFee;
    }
}
