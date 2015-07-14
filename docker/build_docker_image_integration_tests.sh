#!/bin/bash

# Change to the parent directory of this script
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}/../

# Update CLI
echo "Updating client ..."
rm -rf vegadns-cli
mkdir vegadns-cli
cd vegadns-cli
git init
git remote add -t vegadns-cli origin https://github.com/shupp/VegaDNS.git
git fetch
git checkout -b vegadns-cli origin/vegadns-cli
cd ..

echo "Building vegadns2-public-integration-tests image"
docker build -f docker/Dockerfile.integration_tests --no-cache=false \
    -t vegadns2-public-integration-tests .
