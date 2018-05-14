#!/bin/bash

# Operate from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

printf "\nWaiting for VegaDNS-API to be up "
RETURN_CODE=1
COUNT=0
COUNT_LIMIT=${COUNT_LIMIT:-60}
API_URL=${API_URL:-http://localhost:5000}
HOST=${HOST:-http://api:5000} # internal url

while [ $RETURN_CODE -ne 0 ] && [ ${COUNT} ]; do
    RESULTS=$(curl -s -i -o - ${API_URL}/1.0/healthcheck)
    RETURN_CODE=$?
    COUNT=$((COUNT + 1))
    if [ ${RETURN_CODE} -ne 0 ]; then
        sleep 1
    else
        HTTP_CODE=$(echo ${RESULTS} | grep HTTP | awk '{ print $2 }')
        if [ "${HTTP_CODE}" != "200" ]; then
            RETURN_CODE=1
            sleep 1
        fi
    fi
    printf "."
done
printf " done\n"

# exit on failure
set -e

printf "\nRunning integration tests ... \n"
HOST=${HOST} docker-compose \
    -f docker-compose/network.yml \
    -f docker-compose/test-integration.yml \
    run --rm integration_tests

printf "Done.\n"
