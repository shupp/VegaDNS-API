from flask.ext.restful import Resource, request

from vegadns.api.common import Auth


class AbstractEndpoint(Resource):
    auth_required = True

    def __init__(self):
        self.auth = Auth(request, self)
        pass
