pragma solidity ^0.4.0;


import "./safe_math_lib.sol";

// ----------------------------------------------------------------------------
// ERC Token Standard #20 Interface
// https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20-token-standard.md
// ----------------------------------------------------------------------------
contract ERC20Interface {
    function totalSupply() public constant returns (uint); //
    function balanceOf(address tokenOwner) public constant returns (uint balance);
    function transfer(address to, uint tokens) public returns (bool success);
    //function approve(address spender, uint tokens) public returns (bool success);
    //function transferFrom(address from, address to, uint tokens) public returns (bool success);
    //function allowance(address tokenOwner, address spender) public constant returns (uint remaining);
    //event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
    // didn't make functions/events that weren't necessary
    // this makes this contract only partially ERC20 compliant
    event Transfer(address indexed from, address indexed to, uint tokens);
}

contract Burnable {
    event Burn(address indexed burner, uint256 value);
    function burn(uint256 _value) public;
}

contract Issuable {
    event Issue(address indexed to, uint256 value);
    function issue(uint256 tokens, address to) public ;
}


contract arbits is ERC20Interface, Burnable, Issuable {

    using safe_math_lib for uint256;

    string public constant name = "Arbits";
    string public constant symbol = "ARBT";
    uint8 public constant decimals = 0;
    uint256 public current_supply = 0;
    mapping(address=>uint256) public balances;
    mapping(address=>bool) public owners;

    constructor() public {
        owners[msg.sender] = true;
    }

    modifier only_owner() {
        require(owners[msg.sender]);
        _;
    }

    function add_owner(address new_owner) public only_owner {
        owners[new_owner] = true;
    }

    function remove_owner(address old_owner) public only_owner {
        owners[old_owner] = false;
    }

    function totalSupply() public view returns(uint) {
        return current_supply;
    }

    function balanceOf(address tokenOwner) public view returns (uint balance) {
        return balances[tokenOwner];
    }

    function transfer(address to, uint256 tokens) public returns (bool success) {
        require(balances[msg.sender] >= tokens);
        require(tokens >= 0);
        balances[msg.sender] = balances[msg.sender].sub(tokens);
        balances[to] = balances[to].add(tokens);
        emit Transfer(msg.sender, to, tokens);
        return true;
    }

    function burn(uint256 tokens) public {
        require(balances[msg.sender] >= tokens);
        require(tokens >= 0);
        current_supply = current_supply.sub(tokens);
        balances[msg.sender] = balances[msg.sender].sub(tokens);
        emit Burn(msg.sender, tokens);
    }

    function issue(uint256 tokens, address to) public only_owner {
        balances[to] = balances[to].add(tokens);
        current_supply = current_supply.add(tokens);
        emit Issue(to, tokens);
    }
}
