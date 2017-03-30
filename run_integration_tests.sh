#!/bin/bash

printf "Building VegaDNS-CLI ...\n"
docker build -t vegadns-cli https://github.com/shupp/VegaDNS-CLI.git

printf "\nStopping any existing containers ...\n"
API_URL=${API_URL:-http://localhost:5000} docker-compose down || exit 1

printf "\nStarting fresh ones\n"
API_URL=${API_URL:-http://localhost:5000} docker-compose up -d || exit 1

printf "\nwaiting for mysql "
RETURN_CODE=1
while [ $RETURN_CODE -ne 0 ]; do
    docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret -e QUIT vegadns >/dev/null 2>&1
    RETURN_CODE=$?
    sleep 1
    printf "."
done
printf " done\n"

# exit on failure
set -e

printf "\nSeeding data ...\n"
docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/create_tables.sql
docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/data.sql

printf "\nRunning integration tests ...\n"
docker run -e NAMESERVER=client -e HOST=http://api:5000 --net vegadnsapi_vegadns_net vegadns-cli

printf "\nCleaning up ...\n"
API_URL=${API_URL:-http://localhost:5000} docker-compose down
