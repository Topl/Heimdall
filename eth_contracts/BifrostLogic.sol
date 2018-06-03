pragma solidity ^0.4.23;

import "./BifrostStorage.sol";

library BifrostLogic {

    /// editors
    function editUsers(address bifrostStorage, address _ethAdrs, string _toplAdrs, uint256 _balance) internal {
        BifrostStorage(bifrostStorage).editVar_users(_ethAdrs, _toplAdrs, _balance);
    }

    function editInProgress(address bifrostStorage, address _ethAdrs, uint256 _amount) internal {
        BifrostStorage(bifrostStorage).editVar_inProgress(_ethAdrs, _amount);
    }

    function editMinWithdrawalAmount(address bifrostStorage, uint256 _minWithdrawalAmount) internal {
        BifrostStorage(bifrostStorage).editVar_minWithdrawalAmount(_minWithdrawalAmount);
    }

    function editWithdrawalFee(address bifrostStorage, uint256 _withdrawalFee) internal {
        BifrostStorage(bifrostStorage).editVar_withdrawalFee(_withdrawalFee);
    }

    function editDepositFee(address bifrostStorage, uint256 _depositFee) internal {
        BifrostStorage(bifrostStorage).editVar_depositFee(_depositFee);
    }

    /// loaders
    function loadUsers_keyValue(address bifrostStorage, address _ethAdrs) view internal returns(address, string, uint256){
        (string memory a, uint256 b) = BifrostStorage(bifrostStorage).loadVar_users_keyValue(_ethAdrs);
        return (_ethAdrs, a, b);
    }

    function loadInProgress_keyValue(address bifrostStorage, address _ethAdrs) view internal returns(address, uint256){
        uint256 amount = BifrostStorage(bifrostStorage).loadVar_inProgress_keyValue(_ethAdrs);
        return (_ethAdrs, amount);
    }

    function loadMinWithdrawalAmount(address bifrostStorage) view internal returns(uint256) {
        return BifrostStorage(bifrostStorage).loadVar_minWithdrawalAmount();
    }

    function loadWithdrawalFee(address bifrostStorage) view internal returns(uint256) {
        return BifrostStorage(bifrostStorage).loadVar_withdrawalFee();
    }

    function loadDepositFee(address bifrostStorage) view internal returns(uint256) {
        return BifrostStorage(bifrostStorage).loadVar_depositFee();
    }
}
