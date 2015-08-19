from flask import Flask, make_response
from flask_restful import abort, request
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


@endpoint
class Logout(AbstractEndpoint):
    auth_types = ["cookie"]
    route = '/logout'

    def post(self):
        response = make_response('{"status": "ok"}')
        response.mimetype = 'application/json'
        response.set_cookie('vegadns', "", expires=0)

        return response
