import json

from mock import MagicMock

import peewee

from tests.endpoints import AbstractEndpointTest
import vegadns.api.endpoints.apikey
from vegadns.api import app


class TestApiKey(AbstractEndpointTest):
    def test_get_success(self):
        k1 = '7084f356f7ca2761ee6af2b884037c4cda1233c7f6548566f9049e904acfa82a'
        s1 = 'bc4a5565e685d76961db39af80c1f398cd4856fbf06c4c3ffae8c86aef0504fc'

        mock_apikey_one = {
            'apikey_id': 1,
            'account_id': 0,
            'key': k1,
            'secret': s1,
            'description': 'my api key 1',
            'deleted': 0
        }
        mock_model_one = MagicMock()
        mock_model_one.to_dict = MagicMock(return_value=mock_apikey_one)

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = MagicMock(
            return_value=mock_model_one
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'GET',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")

        self.assertEqual(decoded['apikey']['apikey_id'], 1)
        self.assertEqual(decoded['apikey']['key'], k1)
        self.assertEqual(decoded['apikey']['secret'], s1)
        self.assertEqual(decoded['apikey']['deleted'], 0)

    def test_get_failure(self):
        mock = MagicMock()
        mock.side_effect = peewee.DoesNotExist('Not found')

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = mock

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'GET',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "404 NOT FOUND")

    def test_put_success(self):
        k1 = '7084f356f7ca2761ee6af2b884037c4cda1233c7f6548566f9049e904acfa82a'
        s1 = 'bc4a5565e685d76961db39af80c1f398cd4856fbf06c4c3ffae8c86aef0504fc'

        mock_saved = {
            'apikey_id': 1,
            'account_id': 0,
            'key': k1,
            'secret': s1,
            'description': 'my api key 1',
            'deleted': 0
        }
        mock_model_one = MagicMock()
        mock_model_one.to_dict = MagicMock(return_value=mock_saved)
        mock_model_one.save = MagicMock()

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = MagicMock(
            return_value=mock_model_one
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'PUT',
            'test@test.com',
            'test',
            {'description': 'my api key 1', 'deleted': 0}
        )
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")

        self.assertEqual(decoded['apikey']['apikey_id'], 1)
        self.assertEqual(decoded['apikey']['key'], k1)
        self.assertEqual(decoded['apikey']['secret'], s1)
        self.assertEqual(decoded['apikey']['description'], 'my api key 1')
        self.assertEqual(decoded['apikey']['deleted'], 0)

    def test_put_failure(self):
        mock = MagicMock()
        mock.side_effect = peewee.DoesNotExist('Not found')

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = mock

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'PUT',
            'test@test.com',
            'test',
            {'description': 'my api key 1', 'deleted': 0}
        )
        self.assertEqual(response.status, "404 NOT FOUND")

    def test_delete_success(self):
        mock_model_one = MagicMock()
        mock_model_one.save = MagicMock()

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = MagicMock(
            return_value=mock_model_one
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'DELETE',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")

    def test_delete_failure(self):
        mock = MagicMock()
        mock.side_effect = peewee.DoesNotExist('Not found')

        vegadns.api.endpoints.apikey.ApiKey.get_apikey = mock

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys/1',
            'DELETE',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "404 NOT FOUND")
