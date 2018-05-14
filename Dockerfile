FROM alpine:latest

ENV API_PORT 8000

ADD . /opt/vegadns

RUN apk --update add python py-gunicorn py-setuptools
# Removing these packages in the RUN keeps the image small (~70MB)
RUN apk --update add --virtual build-dependencies py-pip python-dev libffi-dev build-base \
  && pip install -r /opt/vegadns/requirements.txt \
  && apk del build-dependencies

WORKDIR /opt/vegadns
CMD python docker/templates/config.py > /opt/vegadns/vegadns/api/config/local.ini \
  && gunicorn --reload --access-logfile - --error-logfile - --workers=25 run:app -b 0.0.0.0:${API_PORT}

EXPOSE ${API_PORT}
