#!/bin/bash

set -e

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

# Update UI
echo "Updating ui ..."
rm -rf vegadns-ui
mkdir vegadns-ui
cd vegadns-ui
git init
git remote add -t vegadns-ui origin https://github.com/shupp/VegaDNS.git
git fetch
git checkout -b vegadns-ui origin/vegadns-ui
cd ..

docker build -f docker/Dockerfile --no-cache=false -t vegadns2-public .
