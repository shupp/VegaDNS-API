import unittest

from vegadns.api.models.apikey import ApiKey
import peewee


class TestApiKey(unittest.TestCase):
    def test_generate_success(self):
        apikey = ApiKey()

        apikey.deleted = 0

        apikey.generate()
        self.assertIsNone(apikey.validate())

    def test_validate_fail_deleted_incorrect(self):
        apikey = ApiKey()

        apikey.deleted = 2
        apikey.generate()
        with self.assertRaises(Exception) as cm:
            apikey.validate()
        self.assertEquals('deleted must be 1 or 0', str(cm.exception))

    def test_validate_fail_invalid_key(self):
        apikey = ApiKey()

        apikey.generate()
        apikey.key = 'foobar'
        with self.assertRaises(Exception) as cm:
            apikey.validate()
        self.assertEquals('Invalid key', str(cm.exception))

    def test_validate_fail_invalid_secret(self):
        apikey = ApiKey()

        apikey.generate()
        apikey.secret = 'foobar'
        with self.assertRaises(Exception) as cm:
            apikey.validate()
        self.assertEquals('Invalid secret', str(cm.exception))
