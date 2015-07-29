import logging
import uuid
import os

from flask import Flask
from flask.ext.restful import Resource, Api


app = Flask(__name__)


if not bool(os.environ.get('DEBUG', None)):
    app.logger.addHandler(logging.StreamHandler())


class VegaDNSApi(Api):
    def handle_error(self, e):
        # Bubble up exceptions with a code set
        if hasattr(e, 'code'):
            return super(VegaDNSApi, self).handle_error(e)

        # Handle unexpected exceptions
        app.logger.exception(e)
        return self.make_response({
            "code": 500,
            "message": "An unexpected error occured"
        }, 500)


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
