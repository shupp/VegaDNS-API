import json
import unittest

from mock import MagicMock

import vegadns.api.endpoints.records
import vegadns.api.models.record
from vegadns.api import app


class TestRecords(unittest.TestCase):
    def setUp(self):
        # Use Flask's test client
        self.test_app = app.test_client()

    def test_get_success(self):
        record_one = vegadns.api.models.record.Record()

        record_one.distance = 0
        record_one.domain_id = 1
        record_one.host = "1.b.vegadns.ubuntu"
        record_one.port = None
        record_one.record_id = 8
        record_one.ttl = 3600
        record_one.type = "A"
        record_one.val = "1.2.3.4"
        record_one.weight = None

        record_two = vegadns.api.models.record.Record()

        record_two.distance = 0
        record_two.domain_id = 1
        record_two.host = "hostmaster.test3.com:ns1.vegadns.ubuntu"
        record_two.port = None
        record_two.record_id = 9
        record_two.ttl = 86400
        record_two.type = "S"
        record_two.val = "16384:2048:1048576:2560"
        record_two.weight = None

        vegadns.api.endpoints.records.Records.get_record_list = MagicMock(
            return_value=[record_one, record_two]
        )

        response = self.test_app.get('/records?domain_id=1')
        self.assertEqual(response.status, "200 OK")

        decoded = json.loads(response.data)
        self.assertEqual(decoded['status'], "ok")
        self.assertEqual(decoded['records'][0]['record_id'], 8)
        self.assertEqual(decoded['records'][0]['record_type'], 'A')
        self.assertEqual(decoded['records'][1]['record_id'], 9)
        self.assertEqual(decoded['records'][1]['record_type'], 'SOA')
