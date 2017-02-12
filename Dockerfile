FROM alpine:latest

ENV VEGADNS_CLI master
ENV VEGADNS_API master

RUN apk add --update py-pip

# Save 20MB by removing git when we are done
RUN apk add --update git \
  && pip install git+https://github.com/shupp/VegaDNS-CLI.git@${VEGADNS_CLI} \
  && apk del git

ADD . /opt/vegadns

# Removing these packages in the RUN shrinks the image by 200MB
RUN apk --update add --virtual build-dependencies python-dev libffi-dev build-base \
  && pip install -r /opt/vegadns/requirements.txt \
  && apk del build-dependencies

CMD cd /opt/vegadns/ \
  && python docker/templates/config.py > /opt/vegadns/vegadns/api/config/local.ini \
  && python run.py

EXPOSE 5000
