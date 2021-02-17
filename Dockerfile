FROM alpine:latest

ENV API_PORT 8000
ENV WORKERS 25
ENV VENV_DIR /opt/venv

ADD . /opt/vegadns

RUN apk --update add python3 py3-setuptools
# Removing these packages in the RUN keeps the image small (~70MB)
RUN apk --update add --virtual build-dependencies py3-pip python3-dev libffi-dev build-base \
  rust cargo openssl-dev \
  && python3 -m venv ${VENV_DIR} \
  && (source ${VENV_DIR}/bin/activate && pip3 install -U pip && pip3 install -r /opt/vegadns/requirements.txt) \
  && apk del build-dependencies

WORKDIR /opt/vegadns
ENTRYPOINT /opt/vegadns/entrypoint.sh

EXPOSE ${API_PORT}
