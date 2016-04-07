import time

import peewee
from flask import Flask, redirect, url_for, make_response
from flask.ext.restful import abort, request

from vegadns.api import endpoint
import vegadns.api.email
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.validate import Validate
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.password_reset_token import \
    PasswordResetToken as ModelToken


@endpoint
class PasswordResetTokens(AbstractEndpoint):
    route = '/password_reset_tokens'

    auth_types = []
    auth_required = False

    def post(self):
        email = request.form.get("email", None)

        if email is None:
            abort(400, message="email is required")

        if not Validate().email(email):
            abort(400, message="invalid email address")

        try:
            account = ModelAccount.get(ModelAccount.email == email)
        except peewee.DoesNotExist:
            abort(400, message="email does not exist")

        # create token
        now = round(time.time())

        token = ModelToken()
        token.account_id = account.account_id
        token.token_value = token.generateToken()
        token.date_created = now

        token.save()

        # cleanup old tokens
        oldtokens = ModelToken.delete().where(
            ModelToken.date_created < now - ModelToken.EXPIRE_IN
        )
        oldtokens.execute()

        # prep email data
        name = account.first_name + " " + account.last_name
        url = config.get(
            'ui_server', 'base_url'
        ) + "#passwordReset?token=" + token.token_value
        data = {
            'name': name,
            'url': url,
        }
        body = vegadns.api.email.parseTemplate('password_reset_request', data)
        to = account.email
        subject = "VegaDNS Password Reset Request"

        # send email
        common = vegadns.api.email.common.Common()
        vegadns.api.email.send(to, subject, body)

        return {'status': 'ok'}
