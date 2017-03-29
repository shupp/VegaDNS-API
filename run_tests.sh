#!/bin/sh

apk add py-pip
pip install -r /opt/vegadns/test-requirements.txt

cd /opt/vegadns && nosetests tests
