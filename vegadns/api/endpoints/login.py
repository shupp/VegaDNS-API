import logging

from flask import Flask, make_response, session
from flask_restful import abort, request
import peewee
from werkzeug.exceptions import Unauthorized

from vegadns.api import endpoint
from vegadns.api.common import Auth
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


@endpoint
class Login(AbstractEndpoint):
    auth_required = False
    route = '/login'

    def get(self):
        oidc_conf = config['oidc']
        if oidc_conf.getboolean('enabled'):
            self.auth_required = True
            self.auth_types = ['oidc']

        auth = Auth(request, self)

        if not auth.account and getattr(auth.response, 'location', None):
            # We got a redirect rather than a final verdict
            # If the request is coming from JS, construct a JSON-parsable
            # object
            # TODO: Perhaps it's best to check request.is_json, but the UI is
            # not setting a json content type yet
            if request.args.get("suppress_auth_response_codes") == "true":
                # flask-pyoidc is currently storing the final redirect URL in
                # the session
                # Once https://github.com/zamzterz/Flask-pyoidc/issues/99 is
                # solved we would no longer need to muck with the session
                # internals
                if oidc_conf.get('ui_endpoint'):
                    session['destination'] = oidc_conf['ui_endpoint']
                return {
                    "status": "redirect",
                    "location": auth.response.location
                }
            else:
                return auth.response

        if not auth.account:
            try:
                auth.cookie_authenticate()
            except Unauthorized:
                return abort(401, message="not logged in")

        return {
            "status": "ok",
            "account": auth.account.to_clean_dict()
        }

    def post(self):
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email is None or password is None:
            return abort(400, message="email and password required")

        if not Validate().email(email):
            return abort(400, message="invalid email")

        try:
            account = ModelAccount.get(
                ModelAccount.email == email,
                ModelAccount.status == 'active'
            )
        except peewee.DoesNotExist:
            return abort(401, message="invalid email or password")

        # check password!
        if not account.check_password(password):
            return abort(401, message="invalid email or password")

        # update to bcrypt
        if account.get_password_algo() != "bcrypt":
            account.set_password(password)
            account.save()

        user_agent = request.headers.get('User-Agent')
        generated_cookie = account.generate_cookie_value(account, user_agent)

        data = {
            "status": "ok",
            "account": account.to_clean_dict()
        }
        response = make_response(self.serialize(data))
        response.mimetype = 'application/json'
        response.set_cookie('vegadns', generated_cookie)

        return response
