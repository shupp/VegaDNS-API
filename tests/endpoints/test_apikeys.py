import json

from mock import MagicMock

from tests.endpoints import AbstractEndpointTest
import vegadns.api.endpoints.apikeys
from vegadns.api import app


class TestApiKeys(AbstractEndpointTest):
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

        k2 = 'c69c30d355dd7c8ab3ecae9c005701a51d30e7c3af1855f1f1be3c7919b2b2c1'
        s2 = 'eebd89e6beae70d24653edbf3b69ad28ecbaa0e877ff60d92f8f07d9130c00cf'

        mock_apikey_two = {
            'apikey_id': 2,
            'account_id': 0,
            'key': k2,
            'secret': s2,
            'description': 'my api key 2',
            'deleted': 0
        }
        mock_model_two = MagicMock()
        mock_model_two.to_dict = MagicMock(return_value=mock_apikey_two)

        vegadns.api.endpoints.apikeys.ApiKeys.get_apikey_list = MagicMock(
            return_value=[mock_model_one, mock_model_two]
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/apikeys',
            'GET',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")

        self.assertEqual(decoded['apikeys'][0]['apikey_id'], 1)
        self.assertEqual(decoded['apikeys'][0]['key'], k1)
        self.assertEqual(decoded['apikeys'][0]['secret'], s1)
        self.assertEqual(decoded['apikeys'][0]['deleted'], 0)

        self.assertEqual(decoded['apikeys'][1]['apikey_id'], 2)
        self.assertEqual(decoded['apikeys'][1]['key'], k2)
        self.assertEqual(decoded['apikeys'][1]['secret'], s2)
        self.assertEqual(decoded['apikeys'][1]['deleted'], 0)

    def test_post_success(self):
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

        vegadns.api.endpoints.apikeys.ApiKeys.create_api_key = MagicMock(
            return_value=mock_model_one
        )

        response = self.open_with_basic_auth(
            '/apikeys',
            'POST',
            'test@test.com',
            'test',
            {'description': 'my api key 1'}
        )
        self.assertEqual(response.status, "201 CREATED")

        decoded = json.loads(response.data)

        self.assertEqual(decoded['status'], "ok")
        self.assertEqual(decoded['apikey']['apikey_id'], 1)
        self.assertEqual(decoded['apikey']['account_id'], 0)
        self.assertEqual(decoded['apikey']['key'], k1)
        self.assertEqual(decoded['apikey']['secret'], s1)
        self.assertEqual(decoded['apikey']['description'], 'my api key 1')
        self.assertEqual(decoded['apikey']['deleted'], 0)
