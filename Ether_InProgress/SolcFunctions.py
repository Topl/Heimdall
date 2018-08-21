from solc import compile_standard, compile_source, compile_files


heimdall_source = str(open("eth_contracts/Heimdall.sol", "r").read())
safe_math_source = str(open("eth_contracts/SafeMath.sol", "r").read())


def get_abi(compiled_sol):
    return compiled_sol["eth_contracts/Heimdall.sol:Heimdall"]["abi"]


def get_bytecode(compiled_sol):
    return compiled_sol["eth_contracts/Heimdall.sol:Heimdall"]["bin"]


def compile_heimdall():
    return compile_files(["eth_contracts/Heimdall.sol", "eth_contracts/SafeMath.sol"])


def abi_heimdall():
    return get_abi(compile_heimdall())


def bytecode_heimdall():
    return get_bytecode(compile_heimdall())