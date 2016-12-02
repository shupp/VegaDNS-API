#!/bin/bash

set -e

if [ "$1" == "test" ]; then
    docker run \
        vegadns2-public \
        /var/www/vegadns2/docker/start.sh \
        test
else
    docker run \
        -p 80:80 \
        -p 53:53/udp \
        vegadns2-public
fi
