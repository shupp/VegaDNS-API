#!/bin/bash

# The entrypoint for the vegadns/apiui image based on nginx
# See docker/Dockerfile.apiui

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

set -e

API_URL=${API_URL:-http://localhost:5000}

# Configure nginx
sed -i -e 's@access_log .*$@access_log /dev/stdout;@' /etc/nginx/nginx.conf
sed -i -e 's@error_log .*$@error_log /dev/stderr;@' /etc/nginx/nginx.conf
echo "daemon off;" >> /etc/nginx/nginx.conf

python3 docker/templates/config.py > /opt/vegadns/vegadns/api/config/local.ini
sed -i -e "s@// var VegaDNSHost = \"http://localhost:5000\";@var VegaDNSHost = \"${API_URL}\";@" /opt/vegadns/vegadns-ui/public/index.html

exec "$@"
