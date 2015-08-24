from flask import Flask, make_response
from flask_restful import abort, request
import peewee

from vegadns.api import endpoint
from vegadns.api.common import Auth, AuthException
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


@endpoint
class Login(AbstractEndpoint):
    auth_required = False
    route = '/login'

    def get(self):
        auth = Auth(request, self)
        try:
            auth.cookie_authenticate()
            return {"status": "ok"}
        except AuthException:
            return abort(401, message="not logged in")

    def post(self):
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email is None or password is None:
            return abort(401, message="email and password required")

        if not Validate().email(email):
            return abort(401, message="invalid email")

        try:
            account = ModelAccount.get(
                ModelAccount.email == email,
                ModelAccount.status == 'active'
            )
        except peewee.DoesNotExist:
            return abort(401, message="invalid email or password")

        # check password!
        if account.hash_password(password) != account.password:
            return abort(401, message="invalid email or password")

        user_agent = request.headers.get('User-Agent')
        generated_cookie = account.generate_cookie_value(account, user_agent)

        response = make_response('{"status": "ok"}')
        response.mimetype = 'application/json'
        response.set_cookie('vegadns', generated_cookie)

        return response
