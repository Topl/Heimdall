pragma solidity ^0.4.23;

import "./SafeMath.sol";
import "./Owned.sol";
import "./BifrostLogic.sol";


contract Bifrost is Owned{

    using SafeMath for uint256; // no overflows
    using BifrostLogic for address;

    address public bifrostStorage; // separate storage for upgradability

    /// storage return structs
    struct user {
        address ethAdrs;
        string  toplAdrs;
        uint256 balance;
    }

    struct inProgressWithdrawal {
        address ethAdrs;
        uint256 amount;
    }

    /// constructor
    constructor(address _bifrostStorage) public payable {
        bifrostStorage = _bifrostStorage;
    }

    bool runThisOnce = true;
    function ownerSetup(string _toplAdrs) onlyOwner public{
        if (runThisOnce) {
            bifrostStorage.editUsers(owner, _toplAdrs, 0);
            runThisOnce = false;
        }
    }

    /// bifrost logic
    /// core functions
    function deposit(string _toplAdrs) public payable {
        /// load storage
        (address account_p1, string memory account_p2, uint256 account_p3) = bifrostStorage.loadUsers_keyValue(msg.sender);
        user memory account = user(account_p1, account_p2, account_p3);
        (address owner_p1, string memory owner_p2, uint256 owner_p3) = bifrostStorage.loadUsers_keyValue(owner);
        user memory ownerAccount = user(owner_p1, owner_p2, owner_p3);
        uint256 depositFee = bifrostStorage.loadDepositFee();

        /// function logic
        if (sha3(account.toplAdrs) != sha3(_toplAdrs)) { // update topl address if new
            account.toplAdrs = _toplAdrs;
        }
        assert(account.balance.add(msg.value).sub(depositFee) > 0); // shouldn't ever throw due to safe math...
        ownerAccount.balance = ownerAccount.balance.add(depositFee);
        account.balance = account.balance.add(msg.value).sub(depositFee);

        /// edit storage
        bifrostStorage.editUsers(ownerAccount.ethAdrs, ownerAccount.toplAdrs, ownerAccount.balance);
        bifrostStorage.editUsers(account.ethAdrs, account.toplAdrs, account.balance);

        /// events
        // DEPOSIT EVENT
    }

    function startWithdrawal(uint256 _amount) public {
        /// load storage
        (address wd_p1, uint256 wd_p2) = bifrostStorage.loadInProgress_keyValue(msg.sender);
        inProgressWithdrawal memory wd = inProgressWithdrawal(wd_p1, wd_p2);

        /// function logic
        assert(validWithdrawal(wd.ethAdrs, wd.amount));
        assert(wd.amount == 0);
        wd.amount = _amount;

        /// edit storage
        bifrostStorage.editInProgress(wd.ethAdrs, wd.amount);

        /// events
        // START WITHDRAWAL EVENT
    }

    function approveWithdrawal(address _ethAdrs, uint256 _amount) onlyOwner public {
        /// load storage
        (address wd_p1, uint256 wd_p2) = bifrostStorage.loadInProgress_keyValue(_ethAdrs);
        inProgressWithdrawal memory wd = inProgressWithdrawal(wd_p1, wd_p2);
        (address account_p1, string memory account_p2, uint256 account_p3) = bifrostStorage.loadUsers_keyValue(_ethAdrs);
        user memory account = user(account_p1, account_p2, account_p3);
        (address owner_p1, string memory owner_p2, uint256 owner_p3) = bifrostStorage.loadUsers_keyValue(owner);
        user memory ownerAccount = user(owner_p1, owner_p2, owner_p3);
        uint256 withdrawalFee = bifrostStorage.loadWithdrawalFee();

        /// function logic
        assert(wd.ethAdrs == _ethAdrs && wd.amount == _amount);
        wd.amount = 0;
        ownerAccount.balance = ownerAccount.balance.add(withdrawalFee);
        account.balance = account.balance.sub(_amount).sub(withdrawalFee);

        /// edit storage
        bifrostStorage.editUsers(ownerAccount.ethAdrs, ownerAccount.toplAdrs, ownerAccount.balance);
        bifrostStorage.editUsers(account.ethAdrs, account.toplAdrs, account.balance);
        bifrostStorage.editInProgress(wd.ethAdrs, wd.amount);

        /// function logic (has to be after edit storage to prevent re-entrant behavior)
        _ethAdrs.transfer(_amount);

        /// events
        // APPROVED WITHDRAWAL
    }

    function denyWithdrawal(address _ethAdrs, uint256 _amount) onlyOwner public {
        /// load storage
        (address wd_p1, uint256 wd_p2) = bifrostStorage.loadInProgress_keyValue(_ethAdrs);
        inProgressWithdrawal memory wd = inProgressWithdrawal(wd_p1, wd_p2);

        /// function logic
        assert(wd.ethAdrs == _ethAdrs && wd.amount == _amount);
    }

    /// helper functions
    function validWithdrawal(address _adrs, uint256 _amount) internal view returns (bool validity) {
        /// load storage
        uint256 minWithdrawalAmount = bifrostStorage.loadMinWithdrawalAmount();
        uint256 withdrawalFee = bifrostStorage.loadWithdrawalFee();
        (address account_p1, string memory account_p2, uint256 account_p3) = bifrostStorage.loadUsers_keyValue(_adrs);
        user memory account = user(account_p1, account_p2, account_p3);

        if (_amount < minWithdrawalAmount) { // min withdrawal check
            return false;
        }

        if (account.balance.sub(withdrawalFee).sub(_amount) < 0) { // debt check
            return false;
        }

        return true;
    }
}
