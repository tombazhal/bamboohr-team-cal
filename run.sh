#!/bin/bash

# Check if a parameter is supplied
if [ -z "$1" ]
then
    echo "The script requires a single parameter that specifies"
    echo " the group of time offs to be used"
    echo "    Example: ./run.sh vac"
    echo "These groups are defined in config.yml file in 'timeoffs' section."
    echo ""
    echo " ! As no parameter supplied, 'vac' will be used"
    echo ""
fi

TIMEOFFS=${1:-vac}

docker compose run -e TIMEOFFS=$TIMEOFFS bhrteamcal