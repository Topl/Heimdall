//////////// GLOBALS ////////////
users = {};


//////////// OWNER ONLY FUNCTIONS ////////////
function issue_eth(topl_address, eth_address, amount) {
    // check that msg.sender is owner
    if (users.topl_address === "undefined") { // new user
        users.topl_address = {"eth_adrs": eth_address, "balance": amount};
    } else { // existing user
        users.topl_address.balance = safeAdd(users.topl_address.balance, amount);
    }
    // create ether assets
    // send ether assets
}


//////////// PUBLIC FUNCTIONS ////////////
function start_transfer(topl_address, eth_address, amount) {

}


//////////// HELPER FUNCTIONS ////////////
function safeAdd(a, b) {
    c = a + b;
    if (c < a || c < b) {
        throw "OVER/UNDERFLOW ERROR";
    } else {
        return c;
    }
}

function safeSub(a, b) {
    c = a - b;
    if (c > a) {
        throw "OVER/UNDERFLOW ERROR";
    } else {
        return c;
    }
}

function safeMul(a, b) {
    c = a * b;
    if (a === 0) {
        return 0;
    }
    if (c / a !== b) {
        throw "OVER/UNDERFLOW ERROR";
    } else {
        return c;
    }
}

function safeDiv(a, b) {
    c = a / b;
    if (b === 0) {
        throw "OVER/UNDERFLOW ERROR";
    } else {
        return c;
    }
}
