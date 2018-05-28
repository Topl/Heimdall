//////////// GLOBALS ////////////
users = {};
transfers = {};


//////////// OWNER ONLY FUNCTIONS ////////////
function issue_eth(topl_address, eth_address, amount) {
    // check that msg.sender is owner
    // create ether assets
    // send ether assets
}

function approve_transfer(topl_address, eth_address, amount) {

}


//////////// PUBLIC FUNCTIONS ////////////
function start_transfer(eth_address, amount) {
    topl_address = msg.sender; // not how this works. just go with it.
    if (transfers.topl_address.active === true) {
        throw "TRANSFER ALREADY IN PROGRESS"
    } else {
        transfers.topl_address = {"eth_adrs": eth_address, "balance": amount, "active": true};
    }
    // broadcast event containing topl_address, eth_address, and amount
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


//////////// EVENTS ////////////

