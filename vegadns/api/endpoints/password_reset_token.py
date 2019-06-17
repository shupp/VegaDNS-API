import time

import peewee
from flask import Flask, redirect, url_for, make_response
from flask_restful import abort, request

from vegadns.api import endpoint
import vegadns.api.email
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.validate import Validate
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.password_reset_token import \
    PasswordResetToken as ModelToken


@endpoint
class PasswordResetToken(AbstractEndpoint):
    route = '/password_reset_tokens/<token>'

    auth_types = []
    auth_required = False

    def get(self, token):
        storedToken = self.fetchToken(token)

        return {
            'status': 'ok',
            'token': storedToken.to_clean_dict()
        }

    def put(self, token):
        """Resets the password and deletes token"""

        storedToken = self.fetchToken(token)
        password = request.form.get("password", None)
        if password is None:
            abort(400, message="password is required")

        account = ModelAccount.get(
            ModelAccount.account_id == storedToken.account_id
        )

        # update password
        account.set_password(password)
        account.save()

        # delete token
        storedToken.delete_instance()

        # prep email data
        name = account.first_name + " " + account.last_name
        data = {'name': name}
        body = vegadns.api.email.parseTemplate('password_was_reset', data)
        to = account.email
        subject = "Your VegaDNS password has been reset"

        # send email
        common = vegadns.api.email.common.Common()
        vegadns.api.email.send(to, subject, body)

        return {'status': 'ok'}

    def fetchToken(self, token):
        if token is None:
            abort(400, message="token is required")

        expired = round(time.time()) - ModelToken.EXPIRE_IN

        try:
            storedToken = ModelToken.get(
                ModelToken.token_value == token,
                ModelToken.date_created > expired
            )
        except peewee.DoesNotExist:
            abort(404, message="token does not exist")

        return storedToken
