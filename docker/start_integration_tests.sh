#!/bin/bash

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

echo "Running integration tests"
nosetests /var/www/vegadns2/vegadns-cli/integration_tests
