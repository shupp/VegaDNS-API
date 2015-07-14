#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
docker run -p 80:80 -p 53:53/udp -v ${DIR}/../sql:/mnt vegadns2-public-integration-tests
