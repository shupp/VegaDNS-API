import logging
import uuid
import os

from flask import Flask
from flask.ext.restful import request, Resource, Api
from flask.ext.cors import CORS


app = Flask(__name__)
cors = CORS(app, supports_credentials=True)


if not bool(os.environ.get('DEBUG', None)):
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
def before_request():
    app.request_id = uuid.uuid4()
