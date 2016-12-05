from flask import Flask, request

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint


@endpoint
class ReleaseVersion(AbstractEndpoint):
    auth_required = False
    route = '/release_version'

    def get(self):
        return {'release_version': '2.0.0'}
