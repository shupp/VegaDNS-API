#!/bin/bash

set -e
set -x

# build environment
rm -rf /var/www/vegadns2/venv
virtualenv /var/www/vegadns2/venv
source /var/www/vegadns2/venv/bin/activate
pip install --upgrade pip
pip install -r /var/www/vegadns2/requirements.txt
pip install uwsgi
