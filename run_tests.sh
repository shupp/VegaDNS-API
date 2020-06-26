#!/bin/sh

set -e

source /opt/venv/bin/activate
cd /opt/vegadns && pycodestyle vegadns tests run.py && nosetests tests
