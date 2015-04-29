import hashlib

from vegadns.api.models.account import Account


class Auth(object):
    def __init__(self, request, endpoint):
        self.account = None
        self.authenticate(request, endpoint)

    def authenticate(self, request, endpoint):
        if endpoint.auth_required is False:
            return True
        else:
            # basic auth for now
            if request.authorization is None:
                raise AuthException('Invalid username or password')

            email = request.authorization.username
            password = request.authorization.password

            account = self.get_account_by_email(email)
            hashed_pass = hashlib.md5(password).hexdigest()

            if account.password != hashed_pass:
                raise AuthException('Invalid email or password')

            self.account = account

    def get_account_by_email(self, email):
        try:
            return Account.get(Account.email == email)
        except Account.DoesNotExist:
            raise AuthException('Account not found')


class AuthException(Exception):
    pass
