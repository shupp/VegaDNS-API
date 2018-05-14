#!/bin/sh

set -e

cd /opt/vegadns && pep8 vegadns tests run.py && nosetests tests
