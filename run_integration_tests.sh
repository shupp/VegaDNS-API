#!/bin/bash

DATE=`date +%s`
export COMPOSE_PROJECT_NAME="vegadnsapiintegration${DATE}"

printf "Building VegaDNS-CLI ...\n"
docker build -t ${COMPOSE_PROJECT_NAME}_vegadns-cli https://github.com/shupp/VegaDNS-CLI.git

printf "\nStarting containers\n"
API_URL=${API_URL:-http://localhost:5000} docker-compose -f docker-compose-integration-test.yml up -d || exit 1

printf "\nwaiting for mysql "
RETURN_CODE=1
while [ $RETURN_CODE -ne 0 ]; do
    docker exec -i ${COMPOSE_PROJECT_NAME}_mysql_1 mysql -h mysql -u vegadns -psecret -e QUIT vegadns >/dev/null 2>&1
    RETURN_CODE=$?
    sleep 1
    printf "."
done
printf " done\n"

# exit on failure
set -e

printf "\nSeeding data ...\n"
docker exec -i ${COMPOSE_PROJECT_NAME}_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/create_tables.sql
docker exec -i ${COMPOSE_PROJECT_NAME}_mysql_1 mysql -h mysql -u vegadns -psecret vegadns < ./sql/data.sql

printf "\nRunning integration tests ...\n"
docker run \
    -e NAMESERVER=client \
    -e HOST=http://api:5000 \
    --net ${COMPOSE_PROJECT_NAME}_vegadns_net \
    --name ${COMPOSE_PROJECT_NAME}_vegadns-cli \
    ${COMPOSE_PROJECT_NAME}_vegadns-cli

printf "\nCleaning up ...\n"
docker rm ${COMPOSE_PROJECT_NAME}_vegadns-cli
docker rmi ${COMPOSE_PROJECT_NAME}_vegadns-cli
API_URL=${API_URL:-http://localhost:5000} docker-compose -f docker-compose-integration-test.yml down
# Need to manually remove this one, not sure why
docker rmi ${COMPOSE_PROJECT_NAME}_api
