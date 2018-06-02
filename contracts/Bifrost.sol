pragma solidity 0.4.23;

import "./SafeMath.sol";
import "./Owned.sol";


contract Bifrost is Owned{

    using SafeMath for uint256; // no overflows

    address bifrostStorage; // separate storage for upgradability

    /// storage return structs
    struct user {
        address ethAdrs;
        string toplAdrs;
        uint256 balance;
    }

    struct inProgressWithdrawal {
        address ethAdrs;
        uint256 amount;
    }

    /// constructor
    constructor(address _bifrostStorage) public {
        bifrostStorage = _bifrostStorage;
    }

    /// bifrost logic
        /// core functions
    function deposit(string _toplAdrs) public payable {
        /// load storage
        user account = loadUsers_keyValue(msg.sender);
        user ownerAccount = loadUsers_keyValue(owner);
        uint256 depositFee = loadDepositFee();

        /// function logic
        if (account.toplAdrs != _toplAdrs) { // update topl address if new
            account.toplAdrs == _toplAdrs;
        }
        assert(account.balance.add(msg.value).sub(depositFee) > 0); // shouldn't ever throw due to safe math...
        ownerAccount.balance = ownerAccount.balance.add(depositFee);
        account.balance = account.balance.add(msg.value).sub(depositFee);

        /// edit storage
        editUsers(ownerAccount.ethAdrs, ownerAccount.toplAdrs, ownerAccount.balance);
        editUsers(account.ethAdrs, account.toplAdrs, account.balance);

        /// events
        // DEPOSIT EVENT
    }

    function startWithdrawal(uint256 _amount) public {
        /// load storage
        inProgressWithdrawal wd = loadInProgress_keyValue(msg.sender);

        /// function logic
        assert(validWithdrawal);
        assert(wd.amount == 0);
        wd.amount = _amount;

        /// edit storage
        editInProgress(wd.ethAdrs, wd.amount);

        /// events
        // START WITHDRAWAL EVENT
    }

    function approveWithdrawal(address _ethAdrs, uint256 _amount) ownerOnyly public {
        /// load storage
        inProgressWithdrawal wd = loadInProgress_keyValue(_ethAdrs);
        user account = loadUsers_keyValue(_ethAdrs);

        /// function logic
        assert(wd.ethAdrs == _ethAdrs && wd.amount == _amount);
        wd.amount = 0;
        account.


    }

    function approve_withdrawal(address user_adrs, uint256 amount) public only_owner { //
        assert(in_progress_wds[user_adrs] == amount); // make sure the tx is what the owner thinks it's signing off on
        receiver.transfer(amount); // do it
        in_progress_wds[user_adrs] = 0; // reset withdrawal to allow for future withdrawals
        users[user_adrs].balance = users[user_adrs].balance.sub(amount).sub(withdrawal_fee); // subtract from user account balance
        users[owner].balance = users[owner].balance.add(withdrawal_fee);
        emit e_withdrawal_approved(user_adrs, users[user_adrs].topl_adrs, amount, withdrawal_fee); // event
    }

        /// helper functions
    function validWithdraw(address _adrs, uint256 _amount) internal view returns (bool validity) {
        /// load storage
        uint256 minWithdrawalAmount = loadMinWithdrawalAmount();
        uint256 withdrawalFee = loadWithdrawalFee();
        user account = loadUsers_keyValue(_adrs);

        if (_amount.sub(withdrawalFee) < minWithdrawalAmount) { // min withdrawal check
            return false;
        }

        if (account.balance.sub(withdrawalFee).sub(_amount) < 0) { // debt check
            return false;
        }

        return true;
    }



    /// bifrost storage edit & load functions
        /// editors
    function editUsers(address _ethAdrs, string _toplAdrs, uint256 _balance) internal {
        bifrostStorage.call(bytes4(sha3("editVar_users(address,string,uint256)")), _ethAdrs, _toplAdrs, _balance);
    }

    function editInProgress(address _ethAdrs, uint256 _amount) internal {
        bifrostStorage.call(bytes4(sha3("editVar_inProgress(address,uint256)")), _ethAdrs, _amount);
    }

    function editMinWithdrawalAmount(uint256 _minWithdrawalAmount) internal {
        bifrostStorage.call(bytes4(sha3("editVar_minWithdrawalAmount(uint256)")), _minWithdrawalAmount);
    }

    function editWithdrawalFee(uint256 _withdrawalFee) internal {
        bifrostStorage.call(bytes4(sha3("editVar_withdrawalFee(uint256)")), _withdrawalFee);
    }

    function editDepositFee(uint256 _depositFee) internal {
        bifrostStorage.call(bytes4(sha3("editVar_depositFee(uint256)")), _depositFee);
    }

        /// loaders
    function loadUsers_keyValue(address _ethAdrs) internal {
        var data = bifrostStorage.call(bytes4(sha3("loadVar_users_keyValue(address)")), _ethAdrs);
        return user(_ethAdrs, data[0], data[1]);
    }

    function loadInProgress_keyValue(address _ethAdrs) internal {
        var data = bifrostStorage.call(bytes4(sha3("loadVar_inProgress_keyValue(address)")), _ethAdrs);
        return inProgressWithdrawal(_ethAdrs, data);
    }

    function loadMinWithdrawalAmount() internal {
        return bifrostStorage.call(bytes4(sha3("loadVar_minWithdrawalAmount()")));
    }

    function loadWithdrawalFee() internal {
        return bifrostStorage.call(bytes4(sha3("loadVar_withdrawalFee()")));
    }

    function loadDepositFee() internal {
        return bifrostStorage.call(bytes4(sha3("loadVar_depositFee()")));
    }

}
