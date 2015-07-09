import re
import time

import peewee

from vegadns.api.config import config
from vegadns.api.models.account import Account
from vegadns.api.models.oauth_access_token import OauthAccessToken


class Auth(object):
    def __init__(self, request, endpoint):
        self.account = None
        self.request = request
        self.endpoint = endpoint
        self.authenticate()

    def authenticate(self):
        if self.endpoint.auth_required is False:
            return True

        # determine auth
        auth_header = self.request.headers.get('Authorization', None)
        if auth_header is None:
            # check if ip auth is allowed
            if "ip" in self.endpoint.auth_types:
                return self.ip_authenticate()

            raise AuthException

        p = re.compile('^Bearer[ ]+(.*$)')
        match = p.findall(auth_header)
        if match:
            if "oauth" in self.endpoint.auth_types:
                return self.oauth_authenticate(match[0])
        else:
            if "basic" in self.endpoint.auth_types:
                return self.basic_authenticate()

        raise AuthException

    def oauth_authenticate(self, token):
        account = self.get_account_by_oauth_token(token)
        self.account = account

    def basic_authenticate(self):
        # basic auth for now
        if self.request.authorization is None:
            raise AuthException('Invalid username or password')

        email = self.request.authorization.username
        password = self.request.authorization.password

        account = self.get_account_by_email(email)
        hashed_pass = account.hash_password(password)

        if account.password != hashed_pass:
            raise AuthException('Invalid email or password')

        self.account = account

    def get_account_by_email(self, email):
        try:
            return Account.get(
                Account.email == email,
                Account.status == 'active'
            )
        except peewee.DoesNotExist:
            raise AuthException('Account not found')

    def get_account_by_oauth_token(self, token):
        now = int(time.time())
        try:
            access_token = OauthAccessToken.get(
                OauthAccessToken.access_token == token,
                OauthAccessToken.expires_at > now
            )
        except peewee.DoesNotExist:
            raise AuthException('invalid_token')

        try:
            return Account.get(
                Account.account_id == access_token.account_id,
                Account.status == 'active'
            )
        except peewee.DoesNotExist:
            raise AuthException('Account not found')

    def ip_authenticate(self):
        ip = self.request.remote_addr
        trusted = config.get('ip_auth', 'trusted_ips')
        if not trusted:
            raise AuthException('IP not authorized: ' + ip)

        if ip != trusted and ip not in ",".split(trusted):
            raise AuthException('IP not authorized: ' + ip)


class AuthException(Exception):
    code = 401
