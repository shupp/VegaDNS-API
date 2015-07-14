#!/bin/bash

# Change to the parent directory of this script
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}/../

docker build -f docker/Dockerfile --no-cache=false -t vegadns2-public .
