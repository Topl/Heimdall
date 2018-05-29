pragma solidity ^0.4.23;


import "./SafeMath.sol";


contract Firewire {


    //////////// LIBRARIES ////////////
    using SafeMath for uint; // NO OVERFLOWS


    //////////// STRUCTS ////////////
    struct user {
        string topl_adrs;
        uint balance;
    }


    //////////// GLOBALS ////////////
    address private owner; // contract owner for // can be changed later
    mapping(address => user) private users; // user address to user balance mapping
    mapping(address => uint) private in_progress_wds; // partially signed withdrawals
    uint private min_wd_amount; // can be changed later
    uint private withdrawal_fee;
    uint private deposit_fee;


    //////////// CONSTRUCTOR ////////////
    constructor(string topl_address) public {
        owner = msg.sender;
        min_wd_amount  = 3141592653589793;
        deposit_fee = 0;
        withdrawal_fee = 0;
        users[owner].topl_adrs = topl_address;
        users[owner].balance = 0;
    }

    //////////// FALLBACK ////////////
    function() public payable { emit e_fallback(msg.sender, msg.value); } // can't make this a address.send because of reentrancy


    //////////// CORE FUNCTIONS ////////////
    function deposit(string topl_address) public payable {
        assert(users[msg.sender].balance.add(msg.value) > users[msg.sender].balance); // overflow check because i'm paranoid
        assert(users[msg.sender].balance.add(msg.value).sub(deposit_fee) > min_wd_amount); // need more than the minimum
        users[msg.sender].balance = users[msg.sender].balance.add(msg.value).sub(deposit_fee);
        users[owner].balance = users[owner].balance.add(deposit_fee);
        users[msg.sender].topl_adrs = topl_address;
        emit e_deposit(msg.sender, users[msg.sender].topl_adrs, msg.value, users[msg.sender].balance, deposit_fee); // event
    }

    function start_withdrawal(uint amount) public {
        assert(valid_withdrawal(msg.sender, amount));
        in_progress_wds[msg.sender] = amount; // add to pending wds
        emit e_withdrawal_started(msg.sender, amount); // event
    }

    function approve_withdrawal(address user_adrs, uint amount) public only_owner { //
        assert(in_progress_wds[user_adrs] == amount); // make sure the tx is what the owner thinks it's signing off on
        execute_withdrawal(user_adrs, amount); // do it
        in_progress_wds[user_adrs] = 0; // reset withdrawal to allow for future withdrawals
        users[user_adrs].balance = users[user_adrs].balance.sub(amount).sub(withdrawal_fee); // subtract from user account balance
        users[owner].balance = users[owner].balance.add(withdrawal_fee);
        emit e_withdrawal_approved(user_adrs, users[user_adrs].topl_adrs, amount, withdrawal_fee); // event
    }

    function deny_withdrawal(address user_adrs, uint amount) public only_owner {
        assert(in_progress_wds[user_adrs] == amount); // make sure the tx is what the owner thinks it's signing off on
        in_progress_wds[user_adrs] = 0; // reset withdrawal to allow for future withdrawals
        emit e_withdrawal_denied(user_adrs, amount); // event
    }


    //////////// HELPER FUNCTIONS ////////////
    function get_balance_from_eth_address() public view returns (uint balance){
        return users[msg.sender].balance;
    }

    function get_topl_address() public view returns (string topl_address) {
        return users[msg.sender].topl_adrs;
    }

    function get_withdrawal_status() public view returns (bool withdrawal_status) {
        if (in_progress_wds[msg.sender] > 0) {
            return true;
        } else {
            return false;
        }
    }

    function get_owner_address() public view returns (address o) {
        return owner;
    }

    function get_owner_topl_address() public view returns (string topl_address) {
        return users[owner].topl_adrs;
    }

    function get_owner_balance() public view returns (uint balance) {
        return users[owner].balance;
    }

    function get_deposit_fee() public view returns (uint fee) {
        return deposit_fee;
    }

    function get_withdrawal_fee() public view returns (uint fee) {
        return withdrawal_fee;
    }


    //////////// INTERNAL FUNCTIONS ////////////
    function valid_withdrawal(address adrs, uint amount) internal view returns (bool retVal) {
        assert(amount.sub(withdrawal_fee) > min_wd_amount); // can't withdraw less than the minimum
        assert(users[adrs].balance.sub(amount).sub(withdrawal_fee) >= 0); // can't go into debt
        // NOTE: this allows for users to leave dust behind
        return true;
    }

    function execute_withdrawal(address receiver, uint amount) internal { // NEEDS TO BE INTERNAL TO PREVENT RE-ENTRANCY ATTACKS
        receiver.transfer(amount);
    }


    //////////// OWNER ADJUSTMENT FUNCTIONS ////////////
    function change_owner_eth_address(address new_owner) public only_owner {
        users[new_owner] = users[owner];
        users[owner].balance = 0;
        users[owner].topl_adrs = "NO LONGER OWNER";
    }

    function change_owner_topl_address(string topl_address) public only_owner {
        users[owner].topl_adrs = topl_address;
    }

    function change_min_wd_amount(uint new_min_wd_amount) public only_owner { // REMEMBER THIS IS IN WEI
        min_wd_amount = new_min_wd_amount;
    }

    function change_withdrawal_fee(uint new_withdrawal_fee) public only_owner {
        withdrawal_fee = new_withdrawal_fee;
    }

    function change_deposit_fee(uint new_deposit_fee) public only_owner {
        deposit_fee = new_deposit_fee;
    }

    function payout() public only_owner {
        msg.sender.transfer(users[owner].balance);
        users[owner].balance = 0;
    }

    // NEED TO IMPLEMENT UPGRADABILITY


    //////////// MODIFIERS ////////////
    modifier only_owner {
        require(msg.sender == owner);
        _;
    }


    //////////// EVENTS ////////////
    event e_deposit(address user, string topl_address, uint amount, uint balance, uint fee);
    event e_withdrawal_started(address user, uint amount);
    event e_withdrawal_approved(address user, string topl_address, uint amount, uint fee);
    event e_withdrawal_denied(address user, uint amount);
    event e_fallback(address sender, uint amount);
}

