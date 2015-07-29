from flask import Flask

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint


@endpoint
class HealthCheck(AbstractEndpoint):
    version = None
    auth_required = False
    route = '/healthcheck'

    def get(self):
        return "{'status': 'ok'}"
