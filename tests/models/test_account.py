import unittest

from vegadns.api.models.account import Account


class TestAccount(unittest.TestCase):
    def test_status_validation(self):
        account = Account()

        account.first_name = "Test"
        account.last_name = "User"
        account.email = "user@example.com"
        account.account_type = "senior_admin"

        # good
        account.status = "active"
        self.assertIsNone(account.validate())

        # good
        account.status = "inactive"
        self.assertIsNone(account.validate())

        # bad
        account.status = "foobar"
        with self.assertRaises(Exception) as cm:
            account.validate()
        self.assertEquals('Invalid status: foobar', cm.exception.message)
