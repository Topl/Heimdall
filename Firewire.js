//////////// CONTRACT CLASS WRAP ////////////
var contract = class {
    //////////// GLOBALS ////////////
    this.transfers = {};
    this.owner = contract.owner; // init owner as contract creator (not how this works either)

    //////////// OWNER ONLY FUNCTIONS ////////////
    issue_eth(topl_address, eth_address, amount) {
        if (msg.sender !== owner) { // owner check
            throw "NOT OWNER";
        }
        // create ether assets
        // send ether assets
    }

    approve_transfer(topl_address, eth_address, amount) {
        if (msg.sender !== owner) { // owner check
            throw "NOT OWNER";
        }
        if (this.transfers.topl_address.eth_adrs === eth_address && this.transfers.topl_address.balance === amount) { // check that this transfer is what the owner thinks it is
            this.transfers.topl_address.balance = 0; // reset transfer obj
            this.transfers.topl_address.active = false;
            // broadcast accepted transfer
        } else {
            throw "NOT A VALID TRANSFER";
        }
        // this is called if and only if
        // owner checks that eth_address is a user on the ethereum sidechaining contract
        // then owner checks that that user's listed topl address is the same as the transfer requester's
        // then owner checks that amount is <= to that user's ether balance
    }

    deny_transfer(topl_address, eth_address, amount) {
        if (msg.sender !== owner) { // owner check
            throw "NOT OWNER";
        }
        if (this.transfers.topl_address.eth_adrs === eth_address && this.transfers.topl_address.balance === amount) { // check that this transfer is what the owner thinks it is
            this.transfers.topl_address.balance = 0; // reset transfer obj
            this.transfers.topl_address.active = false;
            // broadcast denied transfer
        } else {
            throw "NOT A VALID TRANSFER";
        }
        // this is called if and only if
        // owner checks that eth_address is a user on the ethereum sidechaining contract and it is not
        // or the owner then checks that that user's listed topl address is the same as the transfer requester's and it is not
        // or the owner then checks that amount is <= to that user's ether balance and it is not
    }


    //////////// PUBLIC FUNCTIONS ////////////
    start_transfer(eth_address) {
        var amount = msg.assets.ether; // not how this works.
        var topl_address = msg.sender; // not how this works either. just go with it.
        if (this.transfers.topl_address.active === true) {
            throw "TRANSFER ALREADY IN PROGRESS"
        } else {
            this.transfers.topl_address = {"eth_adrs": eth_address, "balance": amount, "active": true};
        }
        // broadcast event containing topl_address, eth_address, and amount
    }

    get_transfer_status(topl_address) {
        if (transfers.topl_address.active === true) {
            return true;
        }
        return false;
    }


    //////////// HELPER FUNCTIONS ////////////
    static safeAdd(a, b) {
        c = a + b;
        if (c < a || c < b) {
            throw "OVER/UNDERFLOW ERROR";
        } else {
            return c;
        }
    }

    static safeSub(a, b) {
        c = a - b;
        if (c > a) {
            throw "OVER/UNDERFLOW ERROR";
        } else {
            return c;
        }
    }

    static safeMul(a, b) {
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

    static safeDiv(a, b) {
        c = a / b;
        if (b === 0) {
            throw "OVER/UNDERFLOW ERROR";
        } else {
            return c;
        }
    }
};

