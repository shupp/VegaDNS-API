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
            return self.send_error_response(400, "email and password required")

        if not Validate().email(email):
            return self.send_error_response(400, "invalid email")

        try:
            account = ModelAccount.get(
                ModelAccount.email == email,
                ModelAccount.status == 'active'
            )
        except peewee.DoesNotExist:
            return self.send_error_response(401, "invalid email or password")

        # check password!
        if account.hash_password(password) != account.password:
            return self.send_error_response(401, "invalid email or password")

        user_agent = request.headers.get('User-Agent')
        generated_cookie = account.generate_cookie_value(account, user_agent)

        response = make_response("{'status': 'ok'}")
        response.mimetype = 'application/json'
        response.set_cookie('vegadns', generated_cookie)

        return response

    def send_error_response(self, code, message):
        if request.form.get("suppress_response_codes") == "true":
            response = {
                'status': 'error',
                'response_code': code,
                'message': message
            }
            return response

        abort(code, message=message)
