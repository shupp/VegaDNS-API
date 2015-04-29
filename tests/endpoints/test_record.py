import json

from mock import MagicMock

from tests.endpoints import AbstractEndpointTest
import vegadns.api.endpoints.record
import vegadns.api.models.record


class TestRecord(AbstractEndpointTest):
    def test_get_success(self):
        model = vegadns.api.models.record.Record()

        model.distance = 0
        model.domain_id = 2
        model.host = "hostmaster.test.com:ns1.vegadns.ubuntu"
        model.port = None
        model.record_id = 10
        model.ttl = 86400
        model.type = "S"
        model.val = "16384:2048:1048576:2560"
        model.weight = None

        vegadns.api.endpoints.record.Record.get_record = MagicMock(
            return_value=model
        )

        self.mock_auth('test@test.com', 'test')

        response = self.open_with_basic_auth(
            '/records/10',
            'GET',
            'test@test.com',
            'test'
        )
        self.assertEqual(response.status, "200 OK")
        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")
        self.assertEqual(decoded['record']['record_id'], 10)
        self.assertEqual(decoded['record']['record_type'], 'SOA')
