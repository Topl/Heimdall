pragma solidity 0.4.23;

import "./SafeMath.sol";
import "./Owned.sol";


contract Bifrost is Owned{

    using SafeMath for uint256; // no overflows

    address bifrostStorage; // separate storage for upgradability

    /// constructor
    constructor(address _bifrostStorage) public {
        bifrostStorage = _bifrostStorage;
        min_wd_amount  = 3141592653589793;
        deposit_fee = 0;
        withdrawal_fee = 0;
        users[owner].topl_adrs = topl_address;
        users[owner].balance = 0;
    }

    /// bifrost storage edit functions
    function editInProgress(address _storage, address _ethAdrs, uint256 _amount) {
        _storage.call(bytes4(sha3("editVar_inProgress(address,uint256)")), _ethAdrs, _amount);
    }

    function editMinWithdrawalAmount(address _storage, uint256 _minWithdrawalAmount) {
        _storage.call(bytes4(sha3("editVar_minWithdrawalAmount(uint256)")), _minWithdrawalAmount);
    }

    function editWithdrawalFee(address _storage, uint256 _withdrawalFee) {
        _storage.call(bytes4(sha3("editVar_withdrawalFee(uint256)")), _withdrawalFee);
    }

    function editDepositFee(address _storage, uint256 _depositFee) {
        _storage.call(bytes4(sha3("editVar_depositFee(uint256)")), _depositFee);
    }

}
