#!/bin/sh

set -e

cd /opt/vegadns && pycodestyle vegadns tests run.py && nosetests tests
