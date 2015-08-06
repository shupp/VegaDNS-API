import hashlib
import base64
import unittest
from mock import MagicMock

from vegadns.api import app
import vegadns.api.common
from vegadns.api.models.account import Account


class AbstractEndpointTest(unittest.TestCase):
    def setUp(self):
        # Use Flask's test client
        self.test_app = app.test_client()

    def mock_auth(email, password, active=True):
        account = Account()
        account.email = 'test@test.com'
        account.password = hashlib.md5('test').hexdigest()
        if active is True:
            account.status = 'active'
        else:
            account.status = 'inactive'

        vegadns.api.common.Auth.get_account_by_email = MagicMock(
            return_value=account
        )

    def open_with_basic_auth(self, url, method, email, password, data=None):
        encoded = base64.b64encode(email + ":" + password).decode("ascii")
        url = "/1.0" + url
        print url
        return self.test_app.open(
            url,
            method=method,
            headers={
                'Authorization': 'Basic ' + encoded,
                'Origin': 'test_client'
            },
            data=data
        )
