FROM alpine:latest

ENV API_PORT 8000
ENV WORKERS 25

ADD . /opt/vegadns

RUN apk --update add python3 py3-gunicorn py3-setuptools
# Removing these packages in the RUN keeps the image small (~70MB)
RUN apk --update add --virtual build-dependencies py3-pip python3-dev libffi-dev build-base \
  && pip3 install -r /opt/vegadns/requirements.txt \
  && apk del build-dependencies

WORKDIR /opt/vegadns
CMD python3 docker/templates/config.py > /opt/vegadns/vegadns/api/config/local.ini \
  && gunicorn --reload --access-logfile - --error-logfile - --workers=${WORKERS} run:app -b 0.0.0.0:${API_PORT}

EXPOSE ${API_PORT}
