import json

from mock import MagicMock

from tests.endpoints import AbstractEndpointTest
import vegadns.api.endpoints.domains
from vegadns.api import app


class TestDomains(AbstractEndpointTest):
    def test_get_success(self):
        mock_domain_one = {
            'owner': 0,
            'status': 'active',
            'domain': 'vegadns.org',
            'domain_id': 1
        }
        mock_model_one = MagicMock()
        mock_model_one.to_clean_dict = MagicMock(return_value=mock_domain_one)

        mock_domain_two = {
            'owner': 0,
            'status': 'active',
            'domain': 'vegadns.net',
            'domain_id': 2
        }
        mock_model_two = MagicMock()
        mock_model_two.to_clean_dict = MagicMock(return_value=mock_domain_two)

        domain_list = MagicMock()
        domain_list.__iter__ = MagicMock(
            return_value=iter([mock_model_one, mock_model_two])
        )
        domain_list.count = lambda: 2

        vegadns.api.endpoints.domains.Domains.get_domain_list = MagicMock(
            return_value=domain_list
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/domains',
            'GET',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")
        self.assertEqual(decoded['domains'][0]['domain_id'], 1)
        self.assertEqual(decoded['domains'][0]['domain'], 'vegadns.org')
        self.assertEqual(decoded['domains'][0]['owner'], 0)
        self.assertEqual(decoded['domains'][1]['domain_id'], 2)
        self.assertEqual(decoded['domains'][1]['domain'], 'vegadns.net')
        self.assertEqual(decoded['domains'][1]['owner'], 0)
