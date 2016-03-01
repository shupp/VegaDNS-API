FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

# VegaDNS2 dependencies
RUN apt-get update && apt-get install -y build-essential python-dev python-virtualenv
RUN apt-get update && apt-get install -y uwsgi-plugin-python
RUN apt-get update && apt-get install -y daemontools daemontools-run ucspi-tcp djbdns
RUN apt-get update && apt-get install -y nginx supervisor
RUN apt-get update && apt-get install -y libffi-dev
# for local exports during integration testing
RUN apt-get update && apt-get install -y curl wget

# for npm
RUN curl -sL https://deb.nodesource.com/setup_0.12 | bash -
RUN apt-get -q update && apt-get install -yf nodejs

# Configuration script dependencies
RUN apt-get update && apt-get install -y python-pip
RUN pip install pystache

# create djbdns accounts Gtinydns, Gdnslog
RUN adduser --force-badname --no-create-home --disabled-login --shell /bin/false Gdnslog
RUN adduser --force-badname --no-create-home --disabled-login --shell /bin/false Gtinydns

# For testing
RUN apt-get update && apt-get install -y mysql-server

# Add software files and templates
ADD . /var/www/vegadns2
RUN chmod +x /var/www/vegadns2/docker/buildenv.sh
RUN /var/www/vegadns2/docker/buildenv.sh

# Add install cli deps
RUN pip install --upgrade /var/www/vegadns2/vegadns-cli

# Set up ui deps
RUN chmod +x /var/www/vegadns2/vegadns-ui/build.sh
RUN /var/www/vegadns2/vegadns-ui/build.sh

RUN chown -R www-data:www-data /var/www/vegadns2

# remove default nginx config
RUN rm -f /etc/nginx/sites-enabled/default

RUN tinydns-conf Gtinydns Gdnslog /etc/tinydns 127.0.0.1
RUN ln -s /etc/tinydns /etc/service

# start all the moving pieces
RUN chmod +x /var/www/vegadns2/bin/update-data.sh
RUN chmod +x /var/www/vegadns2/docker/start.sh
CMD ["/var/www/vegadns2/docker/start.sh"]
