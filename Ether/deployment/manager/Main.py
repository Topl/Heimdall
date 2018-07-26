from manager.StateClasses import EthState, ToplState
from manager.GenStates import GenEthState, GenToplState
import sys
import subprocess


def main():
    EthNodeProc = subprocess.Popen("pwd", shell=True)
    # ToplNodeProc = subprocess.Popen("")
    ES = EthState()
    TS = ToplState()
    if len(sys.argv) == 1:
        print("error you didn't give me enough arguments you dumb bitch")
    elif sys.argv[1] == "old_deploy":
        GenEthState(ES)  # needs to be made
        GenToplState(TS)  # needs to be made



if __name__ == "__main__":
    main()
