pragma solidity ^0.4.23;

import "./HeimdallStorage.sol";

library HeimdallLogic {

    /// editors
    function editUsers(address heimdallStorage, address _ethAdrs, string _toplAdrs, uint256 _balance) internal {
        HeimdallStorage(heimdallStorage).editVar_users(_ethAdrs, _toplAdrs, _balance);
    }

    function editInProgress(address heimdallStorage, address _ethAdrs, uint256 _amount) internal {
        HeimdallStorage(heimdallStorage).editVar_inProgress(_ethAdrs, _amount);
    }

    function editMinWithdrawalAmount(address heimdallStorage, uint256 _minWithdrawalAmount) internal {
        HeimdallStorage(heimdallStorage).editVar_minWithdrawalAmount(_minWithdrawalAmount);
    }

    function editWithdrawalFee(address heimdallStorage, uint256 _withdrawalFee) internal {
        HeimdallStorage(heimdallStorage).editVar_withdrawalFee(_withdrawalFee);
    }

    function editDepositFee(address heimdallStorage, uint256 _depositFee) internal {
        HeimdallStorage(heimdallStorage).editVar_depositFee(_depositFee);
    }

    /// loaders
    function loadUsers_keyValue(address heimdallStorage, address _ethAdrs) view internal returns(address, string, uint256){
        (string memory a, uint256 b) = HeimdallStorage(heimdallStorage).loadVar_users_keyValue(_ethAdrs);
        return (_ethAdrs, a, b);
    }

    function loadInProgress_keyValue(address heimdallStorage, address _ethAdrs) view internal returns(address, uint256){
        uint256 amount = HeimdallStorage(heimdallStorage).loadVar_inProgress_keyValue(_ethAdrs);
        return (_ethAdrs, amount);
    }

    function loadMinWithdrawalAmount(address heimdallStorage) view internal returns(uint256) {
        return HeimdallStorage(heimdallStorage).loadVar_minWithdrawalAmount();
    }

    function loadWithdrawalFee(address heimdallStorage) view internal returns(uint256) {
        return HeimdallStorage(heimdallStorage).loadVar_withdrawalFee();
    }

    function loadDepositFee(address heimdallStorage) view internal returns(uint256) {
        return HeimdallStorage(heimdallStorage).loadVar_depositFee();
    }
}
