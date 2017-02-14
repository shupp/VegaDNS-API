import logging
import uuid
import os
import time

from peewee import OperationalError
from flask import Flask
from flask.ext.restful import request, Resource, Api, abort
from flask.ext.cors import CORS

from vegadns.api.db import database


app = Flask(__name__)
cors = CORS(app, supports_credentials=True)

dbConnected = False


if os.environ.get('DEBUG', None) is not "true":
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel('INFO')


class VegaDNSApi(Api):
    def handle_error(self, e):
        # Bubble up exceptions with a code set
        suppress = self.check_suppress_response_codes()
        if hasattr(e, 'code'):
            if e.code == 401 and suppress:
                # Case for JS client and cross origins,
                # use 200 response instead of 401.
                if hasattr(e, 'message') and len(e.message):
                    message = e.message
                else:
                    message = 'Unauthorized'

                response = self.make_response({
                    "status": "error",
                    "code": 401,
                    "message": message
                }, 200)

                return response
            else:
                # Otherwise, use the parent handle_error()
                return super(VegaDNSApi, self).handle_error(e)
        else:
            # Handle unexpected exceptions
            app.logger.exception(e)
            return self.make_response({
                "code": 500,
                "message": "An unexpected error occured"
            }, 500)

    def check_suppress_response_codes(self):
        suppress = False
        if request.args.get("suppress_auth_response_codes") == "true" \
           or request.form.get("suppress_auth_response_codes") == "true":

            suppress = True

        return suppress


api = VegaDNSApi(app)


def endpoint(cls):
    """A shorthand decorator to create an endpoint out of a class."""
    cls_route = getattr(cls, 'route', None)
    cls_version = getattr(cls, 'version', None)

    if cls_route is None:
        raise Exception('A class field "route" is required')

    if cls_version is None:
        path = cls_route
    else:
        path = "/" + str(cls_version) + cls_route

    api.add_resource(cls, path)
    return cls


@api.representation('text/plain')
def output_text(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


@app.before_request
def set_request_id():
    app.request_id = uuid.uuid4()


@app.before_request
def db_connect():
    """ create DB connection """
    global dbConnected

    attempts = 5
    while attempts > 0:
        try:
            # don't open the connection when unit testing
            if app.testing is True:
                return

            database.connect()
            dbConnected = True
            return
        except OperationalError:
            attempts -= 1
            app.logger.info(
                "MySQL connect failure, attempts left %d" % attempts
            )
            if attempts == 0:
                # we ran out of attempts, abort with message
                # raise
                abort(500, message='Unable to connect to database')
            # let's sleep for a second, we need
            # this to carry on. let's wait a second
            time.sleep(1)


@app.teardown_request
def db_disconnect(exception=None):
    """ close DB connection """
    if dbConnected:
        database.close()
