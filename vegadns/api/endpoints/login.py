from flask import Flask, make_response
from flask_restful import abort, request
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


@endpoint
class Login(AbstractEndpoint):
    auth_required = False
    route = '/login'

    def post(self):
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email is None or password is None:
            abort(400, message="email and password required")

        if not Validate().email(email):
            abort(400, message="invalid email")

        try:
            account = ModelAccount.get(
                ModelAccount.email == email,
                ModelAccount.status == 'active'
            )
        except peewee.DoesNotExist:
            abort(401, message="invalid email or password")

        user_agent = request.headers.get('User-Agent')
        generated_cookie = account.generate_cookie_value(account, user_agent)

        response = make_response("{'status': 'ok'}")
        response.set_cookie('vegadns', generated_cookie)

        return response
