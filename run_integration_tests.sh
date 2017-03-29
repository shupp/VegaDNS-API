#!/bin/bash

echo "Building VegaDNS-CLI ..."
docker build -t vegadns-cli https://github.com/shupp/VegaDNS-CLI.git

echo
echo "Stopping any existing containers ..."
API_URL=${API_URL:-http://localhost:5000} docker-compose down || exit 1

echo
echo "Starting fresh ones"
API_URL=${API_URL:-http://localhost:5000} docker-compose up -d || exit 1

echo
echo -n "waiting for mysql "
RETURN_CODE=1
while [ $RETURN_CODE -ne 0 ]; do
    docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret -e QUIT vegadns >/dev/null 2>&1
    RETURN_CODE=$?
    sleep 1
    echo -n .
done
echo " done"

# exit on failure
set -e

echo
echo "Seeding data ..."
docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/create_tables.sql
docker exec -i vegadnsapi_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/data.sql

echo
echo "Running integration tests ..."
docker run -e NAMESERVER=client -e HOST=http://api:5000 --net vegadnsapi_vegadns_net vegadns-cli

echo
echo "Cleaning up ..."
API_URL=${API_URL:-http://localhost:5000} docker-compose down
