#!/bin/bash

set -e

if [ "$1" == "test" ]; then
    echo "In integration test mode"
    TEST=1
else
    TEST=0
fi


if [ $TEST -eq 0 ]; then
    echo "Configuring tinydns IP"
    IP=`ifconfig | grep -A 1 eth0 | sed -ne '2p' | awk '{ print $2 }' | sed -e 's/^addr://'`
    echo ${IP} > /etc/tinydns/env/IP
fi

echo "Starting daemontools for tinydns"
sh -cf '/usr/bin/svscanboot &'

echo "Starting MySQL"
service mysql start

echo "Setting up the vegadns DB"
mysqladmin -u root create vegadns --password=""
mysql --password="" -u root -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON vegadns.* TO vegadns@localhost IDENTIFIED BY 'secret'"
mysql -u root vegadns < /mnt/create_tables.sql
mysql -u root vegadns < /mnt/data.sql

echo "Setting up config files for supervisor, nginx, VegaDNS2"
cp /var/www/vegadns2/docker/templates/supervisor-vegadns2.conf /etc/supervisor/conf.d/vegadns2.conf
cp /var/www/vegadns2/docker/templates/nginx-vegadns2.conf /etc/nginx/sites-enabled/vegadns2
cp /var/www/vegadns2/docker/templates/local.ini /var/www/vegadns2/vegadns/api/config/local.ini
cp /var/www/vegadns2/docker/templates/sudoers.www-data /etc/sudoers.d/vegadns2-www-data
chmod 660 /etc/sudoers.d/vegadns2-www-data

echo "Starting supervisor"
/etc/init.d/supervisor start

echo "Starting nginx"
/etc/init.d/nginx start

echo "Sleeping 4 to wait for supervisor"
/bin/sleep 4

if [ $TEST -eq 1 ]; then
    echo "Running unit tests"
    cd /var/www/vegadns2
    source venv/bin/activate
    make

    # Integration tests
    echo "Running integration tests"
    deactivate
    nosetests vegadns-cli/integration_tests
else
    echo "Ready!"
    /bin/sleep infinity
fi
