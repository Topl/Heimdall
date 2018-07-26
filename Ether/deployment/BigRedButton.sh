#!usr/bin/bash

eval "ganache-cli >/dev/null &"
export GANACHE_PID=$!
if grep -Rq "deployed" manager/deploy.txt
    then
        echo "already deployed"
        python3 main.py old_deploy
        cd manager
        python3 main.py new_deploy
        export PYTHON_PID=$!
        cd ..
    else
        echo "deploying now"
        echo "deployed\n" > manager/deploy.txt
        truffle migrate --network local_testnet --reset >> manager/deploy.txt
        cd manager
        python3 main.py new_deploy
        export PYTHON_PID=$!
        cd ..
fi
kill ${GANACHE_PID}
kill ${PYTHON_PID}

exit