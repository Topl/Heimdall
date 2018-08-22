ContractABI = [
    {
        "constant": False,
        "inputs": [
            {
                "name": "_a",
                "type": "address"
            }
        ],
        "name": "new_owner",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_v",
                "type": "string"
            }
        ],
        "name": "take",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_a",
                "type": "address"
            },
            {
                "name": "_v",
                "type": "uint256"
            }
        ],
        "name": "give",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "name": "sender",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "amount",
                "type": "uint256"
            },
            {
                "indexed": False,
                "name": "receiver",
                "type": "string"
            }
        ],
        "name": "t",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "name": "receiver",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "g",
        "type": "event"
    }
]
