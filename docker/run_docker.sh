#!/bin/bash

COMMAND=""
ARG=""

if [ "$1" == "test" ]; then
    COMMAND="/var/www/vegadns2/docker/start.sh"
    ARG="/var/www/vegadns2/docker/start.sh"
fi

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
docker run \
    -p 80:80 \
    -p 53:53/udp \
    -v ${DIR}/../sql:/mnt \
    vegadns2-public \
    $COMMAND \
    $ARG
