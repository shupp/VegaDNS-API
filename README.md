# VegaDNS API

VegaDNS API, the successor to [VegaDNS](https://github.com/shupp/VegaDNS),  is a REST API for managing DNS records in MySQL for use with [tinydns](http://cr.yp.to/djbdns/blurb/overview.html).  Written in python, it relies on [flask](http://flask.pocoo.org), [flask_restful](https://flask-restful.readthedocs.org/en/0.3.4/), and [peewee](http://peewee.readthedocs.org/en/latest/).  It generally is run using [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/) and [supervisor](http://supervisord.org) behind [nginx](http://nginx.org).  (See the [docker/templates](https://github.com/shupp/VegaDNS-API/tree/master/docker/templates) directory for example configuration files).  It currently supports basic auth, cookies, and [OAuth2 (section 4.4)](https://tools.ietf.org/html/rfc6749#section-4.4) for authentication.

## Supported Clients
There are two supported API clients at this time:

* [VegaDNS-UI](https://github.com/shupp/VegaDNS-UI) - a JavaScript only UI, similar to the old VegaDNS.
* [VegaDNS-CLI](https://github.com/shupp/VegaDNS-CLI) - a command line interface that includes a reusable client library written in python.


## Installation

### Manual setup from a git checkout
If you want to get this up and running from a git checkout quickly, you'll want to use python 2.7.9 or later (3 is not yet tested), and have pip and virtualenv installed.  This assumes you have a mysql server with a database called _vegadns_ created, and write privileges granted.  From there, you can do the following to set up your virtual environment:

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

You'll also need to set up your vegadns/api/config/local.ini file with the following, replacing values with credentials for your mysql database:

```
[mysql]
user = vegadns
password = secret
database = vegadns
host = localhost
```

Lastly, you need to create your database contents.  You can apply the following an empty database:

```
mysql -u vegadns -p -h localhost vegadns < sql/create_tables.sql
mysql -u vegadns -p -h localhost vegadns < sql/data.sql
```

If you are testing a copy of a legacy VegaDNS database, you can just run this instead:

```
mysql -u vegadns -p -h localhost vegadns < sql/data.sql
```

Now that the environment is setup, you can start the built-in flask web server to test below:

```
$ DEBUG=true python run.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
  * Restarting with stat
  ```

## Setup using docker
If you have [docker](http://docker.com) setup, you can build a docker container with the cli and ui built in.  There are scripts in the docker directory to help with this, [build_docker_image.sh](https://github.com/shupp/VegaDNS-API/blob/master/docker/build_docker_image.sh) and [run_docker.sh](https://github.com/shupp/VegaDNS-API/blob/master/docker/run_docker.sh)


## Using
Once installation is complete, you'll probably want to use one of the supported clients above for accessing the api.  If this is a clean install, the test account is test@test.com with a password of "test".  If you're using existing accounts, they should work as well.

# Changes from legacy [VegaDNS](http://github.com/shupp/VegaDNS)

* **New permissions structure**.  Instead of 3 tiers (_senior_admin, group_admin, user_), there is only _senior_admin_ and _user_ tiers (type).  Users can own domains and privileges can now be granted to groups.  This should be a much more flexible architecture.  Currently there is no migration tool for people using the legacy group_admin tier.  If there is much of a need, I can put one together.
* **REST API only**, a JavaScript only UI is available separately [here](https://github.com/shupp/VegaDNS-UI)
* API is written in **python** rather than PHP

# Support
For comments or support, please use the [issue tracker](https://github.com/shupp/VegaDNS-API/issues) on Github.  You may use the [Google Group](https://groups.google.com/forum/#!forum/vegadns) as well for discussions.
