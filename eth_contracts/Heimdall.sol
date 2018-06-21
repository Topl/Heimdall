pragma solidity 0.4.24;


import "./SafeMath.sol";


contract Heimdall {

    using SafeMath for uint256; // no overflows

    mapping(address=>uint256) public withdrawals;
    address public owner;
    uint256 public ownerBalance = 0;
    uint256 public depositFee = 0;
    uint256 public withdrawalFee = 0;
    bool public contractOpen = false;

    constructor() public {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    modifier reqOpen() {
        require(contractOpen);
        _;
    }

    function deposit(string memory _toplAdrs) public payable reqOpen {
        assert(msg.value.sub(depositFee) > 0); // no debt
        ownerBalance = ownerBalance.add(depositFee);
        emit DepositEvent(owner, msg.sender, msg.value, depositFee, _toplAdrs);
    }

    function startWithdrawal(uint256 _amount) public reqOpen {
        assert(_amount.sub(withdrawalFee) > 0); // no debt
        withdrawals[msg.sender] = _amount;
        emit StartWithdrawalEvent(owner, msg.sender, _amount, withdrawalFee);
    }

    function approveWithdrawal(
        address _ethAdrs,
        uint256 _amount,
        uint256 _withdrawalFee
    ) public onlyOwner {
        withdrawals[_ethAdrs] = 0;
        ownerBalance = ownerBalance.add(_withdrawalFee);
        _ethAdrs.transfer(_amount.sub(_withdrawalFee));
        emit ApproveWithdrawalEvent(owner, _ethAdrs, _amount, _withdrawalFee);
    }

    function denyWithdrawal(address _ethAdrs, uint256 _amount, uint256 _withdrawalFee) public onlyOwner {
        withdrawals[_ethAdrs] = 0;
        emit DeniedWithdrawalEvent(owner, _ethAdrs, _amount, _withdrawalFee);
    }

    function setDepositFee(uint256 _fee) public onlyOwner {
        emit SetDepositFeeEvent(owner, depositFee, _fee);
        depositFee = _fee;
    }

    function setWithdrawalFee(uint256 _fee) public onlyOwner {
        emit SetWithdrawalFeeEvent(owner, withdrawalFee, _fee);
        withdrawalFee = _fee;
    }

    function ownerWithdrawal() public onlyOwner {
        emit OwnerWithdrawalEvent(owner, ownerBalance);
        ownerBalance = 0;
        owner.transfer(ownerBalance);
    }

    function toggleContractOpen() public onlyOwner {
        contractOpen = !contractOpen;
        emit ToggleContractOpenEvent(owner, !contractOpen, contractOpen);
    }

    event DepositEvent(
        address ownerAddress,
        address depositerAddress,
        uint256 deposit,
        uint256 depositFee,
        string toplAdrs);

    event StartWithdrawalEvent(
        address ownerAddress,
        address withdrawerAddress,
        uint256 withdrawalAmount,
        uint withdrawalFee);

    event ApproveWithdrawalEvent(
        address ownerAddress,
        address withdrawerAddress,
        uint256 withdrawalAmount,
        uint256 withdrawalFee);

    event DeniedWithdrawalEvent(
        address ownerAddress,
        address withdrawerAddress,
        uint256 withdrawalAmount,
        uint256 withdrawalFee);

    event SetDepositFeeEvent(address ownerAddress, uint256 oldFee, uint256 newFee);
    event SetWithdrawalFeeEvent(address ownerAddress, uint256 oldFee, uint256 newFee);
    event OwnerWithdrawalEvent(address ownerAddress, uint256 withdrawalAmount);
    event ToggleContractOpenEvent(address ownerAddress, bool oldContractOpen, bool newContractOpen);
}
