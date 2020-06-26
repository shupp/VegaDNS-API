#!/bin/sh

VENV_DIR=${VENV_DIR:-/opt/venv}
WORKERS=${WORKERS:-25}
API_PORT=${API_PORT:-8000}

source ${VENV_DIR}/bin/activate
python3 docker/templates/config.py > /opt/vegadns/vegadns/api/config/local.ini
gunicorn --reload --access-logfile - --error-logfile - --workers=${WORKERS} run:app -b 0.0.0.0:${API_PORT}
