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

        /// has to be run after the constructor because the storage contract
        /// has to be given the address of this contract as it's master to
        /// accept any calls
        /// OPEN TO OTHER IDEAS
    bool runThisOnce = true;
    function ownerSetup(string _toplAdrs) onlyOwner public {
        if (runThisOnce) {
            bifrostStorage.editUsers(owner, _toplAdrs, 0);
            runThisOnce = false;
        }
    }

    /// core functionality
    function deposit(string memory _toplAdrs) public payable {
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
        emit deposit_event(msg.sender, msg.value, account.balance, depositFee);
    }

    function startWithdrawal(uint256 _amount) public {
        /// load storage
        (address wd_p1, uint256 wd_p2) = bifrostStorage.loadInProgress_keyValue(msg.sender);
        inProgressWithdrawal memory wd = inProgressWithdrawal(wd_p1, wd_p2);
        uint256 withdrawalFee = bifrostStorage.loadWithdrawalFee();
        (address account_p1, string memory account_p2, uint256 account_p3) = bifrostStorage.loadUsers_keyValue(msg.sender);
        user memory account = user(account_p1, account_p2, account_p3);

        /// function logic
        assert(validWithdrawal(wd.ethAdrs, wd.amount));
        assert(wd.amount == 0);
        wd.amount = _amount;
        uint256 endingValue = account.balance.sub(_amount).sub(withdrawalFee);

        /// edit storage
        bifrostStorage.editInProgress(wd.ethAdrs, wd.amount);

        /// events
        emit startedWithdrawal_event(msg.sender, _amount, endingValue, withdrawalFee);
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
        validWithdrawal(wd.ethAdrs, wd.amount);
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
        emit approvedWithdrawal_event(_ethAdrs, _amount, account.balance, withdrawalFee);
    }

    function denyWithdrawal(address _ethAdrs, uint256 _amount) onlyOwner public {
        /// load storage
        (address wd_p1, uint256 wd_p2) = bifrostStorage.loadInProgress_keyValue(_ethAdrs);
        inProgressWithdrawal memory wd = inProgressWithdrawal(wd_p1, wd_p2);

        /// function logic
        assert(wd.ethAdrs == _ethAdrs && wd.amount == _amount);
        wd.amount = 0;

        /// edit storage
        bifrostStorage.editInProgress(wd.ethAdrs, wd.amount);

        /// events
        emit deniedWithdrawal_event(_ethAdrs, _amount);
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

    function changeToplAddress(string memory _toplAdrs) public {
        /// load storage
        (address p1, string memory p2, uint256 p3) = bifrostStorage.loadUsers_keyValue(msg.sender);
        user memory account = user(p1, p2, p3);

        /// edit storage
        bifrostStorage.editUsers(account.ethAdrs, _toplAdrs, account.balance);

        /// events
        emit changedToplAddress_event(account.ethAdrs, account.balance, p2, account.toplAdrs);
    }

    function changeEthAddress(address _newEthAdrs) public {
        /// load storage
        (address p1, string memory p2, uint256 p3) = bifrostStorage.loadUsers_keyValue(msg.sender);
        user memory account = user(p1, p2, p3);
        user memory newAccount = user(_newEthAdrs, p2, p3);

        /// edit storage
        bifrostStorage.editUsers(account.ethAdrs, "previously used", 0);
        bifrostStorage.editUsers(newAccount.ethAdrs, newAccount.toplAdrs, newAccount.balance);

        /// events
        emit changedToplAddress_event(p2, p3, p1, _newEthAdrs);
    }

    /// owner control functions
    function setDepositFee(uint256 _fee) onlyOwner public {
        uint256 oldFee = bifrostStorage.loadDepositFee();
        bifrostStorage.editDepositFee(_fee);
        emit minWithdrawalAmountSet_event(oldFee, _fee);
    }

    function setWithdrawalFee(uint256 _fee) onlyOwner public {
        uint256 oldFee = bifrostStorage.loadWithdrawalFee();
        bifrostStorage.editWithdrawalFee(_fee);
        emit minWithdrawalAmountSet_event(oldFee, _fee);
    }

    function setMinWithdrawalAmount(uint256 _amount) onlyOwner public {
        uint256 oldAmount = bifrostStorage.loadMinWithdrawalAmount();
        bifrostStorage.editMinWithdrawalAmount(_amount);
        emit minWithdrawalAmountSet_event(oldAmount, _amount);
    }

    /// events
    event deposit_event(address depositer, uint256 depositValue, uint256 endingValue, uint256 depositFeePaid);
    event startedWithdrawal_event(address withdrawer, uint256 withdrawalAmount, uint256 endingValue, uint withdrawalFee);
    event approvedWithdrawal_event(address withdrawer, uint256 withdrawalAmount, uint256 endingValue, uint256 withdrawalFeePaid);
    event deniedWithdrawal_event(address withdrawer, uint256 withdrawalAmount);
    event depositFeeSet_event(uint256 oldFee, uint256 newFee);
    event withdrawalFeeSet_event(uint256 oldFee, uint256 newFee);
    event minWithdrawalAmountSet_event(uint256 oldAmount, uint256 newAmount);
    event changedToplAddress_event(address ethAdrs, uint256 balance, string oldToplAdrs, string newToplAdrs);
    event changedToplAddress_event(string toplAdrs, uint256 balance, address oldEthAdrs, address newEthAdrs);
}
