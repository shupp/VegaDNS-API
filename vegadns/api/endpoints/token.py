from builtins import str
import time
import uuid

import peewee

from flask import Flask, abort, request
from flask.ext.restful import Resource, abort

from vegadns.api.config import config
from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.apikey import ApiKey
from vegadns.api.models.account import Account
from vegadns.api.models.oauth_access_token import OauthAccessToken

from peewee import MySQLDatabase, Model
from lib.shortcuts import model_to_dict


@endpoint
class Token(AbstractEndpoint):
    auth_required = False
    route = '/token'

    def post(self):
        # FIXME - add rate limiting

        # validate request
        grant_type = request.form.get('grant_type', '')
        if grant_type == "":
            abort(400, message="invalid_request")
        if grant_type != 'client_credentials':
            abort(400, message="unsupported_grant_type")

        # validate client (apikey)
        if request.authorization is not None:
            # preferred, use basic authorization
            key = request.authorization.username
            secret = request.authorization.password
        else:
            # alternatively, look in post params
            key = request.form.get('client_id', None)
            secret = request.form.get('client_secret', None)

        if not key or not secret:
            abort(400, message="invalid_request")

        now = int(time.time())
        expire_time = int(config.get('oauth', 'token_expire_time'))

        try:
            apikey = self.get_apikey(key, secret)
        except peewee.DoesNotExist:
            abort(400, message="invalid_client")

        try:
            # look up existing token first, make sure it's good for at least
            # ten minutes
            token = self.get_token(apikey.apikey_id, now + 600)
        except peewee.DoesNotExist:
            # create one if needed
            token = OauthAccessToken()
            token.account_id = apikey.account_id.account_id
            token.apikey_id = apikey.apikey_id
            token.access_token = str(uuid.uuid4())
            token.grant_type = 'client_credentials'
            token.expires_at = now + expire_time
            try:
                token.save()
            except:
                abort(500, 'unable to generate token')

        return {
            'access_token': token.access_token,
            'token_type': 'bearer',
            'expires_in': token.expires_at - now
        }

    def get_token(self, apikey_id, expires_at):
        return OauthAccessToken().get(
                OauthAccessToken.apikey_id == apikey_id,
                OauthAccessToken.expires_at > expires_at
            )

    def get_apikey(self, key, secret):
        return ApiKey().select(ApiKey, Account).join(
                Account,
                on=ApiKey.account_id == Account.account_id
        ).where(
            ApiKey.key == key,
            ApiKey.secret == secret,
            ApiKey.deleted == 0,
            Account.status == 'active'
        ).get()
