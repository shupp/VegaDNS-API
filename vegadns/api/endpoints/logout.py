from flask import Flask, jsonify, current_app
from flask_restful import abort, request

import peewee

from vegadns.api import endpoint
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


@endpoint
class Logout(AbstractEndpoint):
    auth_types = ["cookie", "oidc"]
    route = '/logout'

    def post(self):
        output = {"status":"ok"}
        if config.getboolean('oidc', 'enabled'):
            logout_func = current_app.config['OIDC_AUTH'].oidc_logout(lambda: False)
            response = logout_func()
            if response is not False and getattr(response,'location', None):
                output['redirect'] = response.location

        response = jsonify(output)
        response.set_cookie('vegadns', "", expires=0)

        return response
