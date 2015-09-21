#!/bin/bash

set -e

# Change to the parent directory of this script
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}/../

# Update CLI
echo "Updating client ..."
rm -rf vegadns-cli
git clone https://github.com/shupp/VegaDNS-CLI.git vegadns-cli

# Update UI
echo "Updating ui ..."
rm -rf vegadns-ui
git clone https://github.com/shupp/VegaDNS-UI.git vegadns-ui

docker build -f docker/Dockerfile --no-cache=false -t vegadns2-public .
