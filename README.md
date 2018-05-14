# VegaDNS API

VegaDNS API, the successor to [VegaDNS](https://github.com/shupp/VegaDNS),  is a REST API for managing DNS records in MySQL for use with [tinydns](http://cr.yp.to/djbdns/blurb/overview.html).  Written in python, it relies on [flask](http://flask.pocoo.org), [flask_restful](https://flask-restful.readthedocs.org/en/0.3.4/), and [peewee](http://peewee.readthedocs.org/en/latest/).  It generally is run using [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/) and [supervisor](http://supervisord.org) behind [nginx](http://nginx.org).  (See the [example-configs](example-configs) directory for example configuration files).  It currently supports basic auth, cookies, and [OAuth2 (section 4.4)](https://tools.ietf.org/html/rfc6749#section-4.4) for authentication.

## Supported Clients
There are two supported API clients at this time:

* [VegaDNS-UI](https://github.com/shupp/VegaDNS-UI) - a JavaScript only UI, similar to the old VegaDNS.
* [VegaDNS-CLI](https://github.com/shupp/VegaDNS-CLI) - a command line interface that includes a reusable client library written in python.


## Installation

### Setup using docker compose
The following steps assumes your docker host is "localhost"

    make pull up

Then log in at http://localhost/ with the user "test@test.com" and a password of "test"

If you want to watch logs, say for just api and tinydns, you can do:

    LOGS_ARGS="-f api tinydns" make logs

To shut down, just run

    make down

The above will run the api on port 5000, and the ui on port 80.  If you would like to experiment with the vegadns/apiui image, which runs both components on port 80, you can use the following commands:

    make up apiui
    make down apiui

### Building the vegadns/api or vegadns/apiui images

    make build-api
    make build-apiui

### Manual setup of the api from a git checkout
If you want to get this up and running from a git checkout manually, you'll want to use python 2.7.9 or later (3 is not yet tested), and have pip and virtualenv installed.  This assumes you have a mysql server with a database called _vegadns_ created, and write privileges granted.  From there, you can do the following to set up your virtual environment:

    make venv

You'll also need to set up your vegadns/api/config/local.ini file with the following, replacing values with credentials for your mysql database:

    [mysql]
    user = vegadns
    password = secret
    database = vegadns
    host = localhost

Have a look at [default.ini](vegadns/api/config/default.ini) for a full list of configuration items you may want to override.

Lastly, you need to create your database contents.  You can apply the following an empty database:

    mysql -u vegadns -p -h localhost vegadns < sql/create_tables.sql
    mysql -u vegadns -p -h localhost vegadns < sql/data.sql

If you are testing a copy of a legacy VegaDNS database, you can just run this instead:

    mysql -u vegadns -p -h localhost vegadns < sql/new_tables_only.sql
    mysql -u vegadns -p -h localhost vegadns < sql/alter-01.sql
    mysql -u vegadns -p -h localhost vegadns < sql/alter-02.sql
    mysql -u vegadns -p -h localhost vegadns < sql/alter-03.sql
    mysql -u vegadns -p -h localhost vegadns < sql/data_api_keys_only.sql

Now that the environment is setup, you can start the built-in flask web server to test below:

    $ . venv/bin/activate && DEBUG=true python run.py
     * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
      * Restarting with stat

## Using
Once installation is complete, you'll probably want to use one of the supported clients above for accessing the api.  If this is a clean install, the test account is test@test.com with a password of "test".  If you're using existing accounts, they should work as well.

## Running under uwsgi/supervisor/nginx
The vegadns/api image currently runs under [gunicorn](http://gunicorn.org).  If you want to run
it under uwsgi/supervisor/nginx and alongside the UI like the vegadns/apiui image, see the files in the
[docker/templates](docker/templates) directory, as well as [docker/Dockerfile.apiui](docker/Dockerfile.apiui) and [docker/start.sh](docker/start.sh).

## Tests - running in containers
To run unit tests in a container using docker-compose, just run:

    make test-docker

For integration tests only, run:

    make up test-integration down

## Tests - running locally
To check pep8 compliance and run tests locally, run:

    make test

You can also check code coverage:

    make coverage

or

    make coverage-html

This will call "open" on the coverage html, opening it in your browser.

## Changes from legacy [VegaDNS](http://github.com/shupp/VegaDNS)

* **New permissions structure**.  Instead of 3 tiers (_senior_admin, group_admin, user_), there is only _senior_admin_ and _user_ tiers (type).  Users can own domains and privileges can now be granted to groups.  This should be a much more flexible architecture.  Currently there is no migration tool for people using the legacy group_admin tier.  If there is much of a need, I can put one together.
* **Added tinydns location support**.  If you want to do split horizon dns, you can specify locations and network prefixes for those locations, and then bind records to those locations to serve up different results based on the network the request came from.  If you want to use IPv6 network prefixes, note that djbdns needs to be [patched for IPv6](http://www.fefe.de/dns/).  (If on debian/ubuntu, you can alternately use the already patched dbndns package instead of the djbdns package)
* **Optional push notifications to updaters**.  If you want your tinydns servers to update on demand, you can set up a redis server to handle Pub/Sub messaging.  See [default.ini](vegadns/api/config/default.ini) and [redis_listener.sh](https://github.com/shupp/VegaDNS-UpdateClient/blob/master/redis_listener.sh).
* **REST API only**, a JavaScript only UI is available separately [here](https://github.com/shupp/VegaDNS-UI)
* **Optional global record ACLs** To allow restrictions on integrations with tools like [Let's Encrypt](https://letsencrypt.org), you can now specify certain global labels (i.e. _acme-challenge.DOMAIN) that can be written to by a list of users.  See [default.ini](vegadns/api/config/default.ini) for more details.
* API is written in **python** rather than PHP

## Support
For comments or support, please use the [issue tracker](https://github.com/shupp/VegaDNS-API/issues) on Github.  You may use the [Google Group](https://groups.google.com/forum/#!forum/vegadns) as well for discussions.
