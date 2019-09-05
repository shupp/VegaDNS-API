import unittest

from vegadns.api.models.record import Record
from vegadns.api.models.recordtypes import RecordValueException


class TestRecord(unittest.TestCase):
    def test_hostname_in_domain(self):
        record = Record()

        domain = "foobar.com"
        bad = "wwwfoobar.com"
        good = "www.foobar.com"

        self.assertTrue(record.hostname_in_domain(domain, domain))
        self.assertFalse(record.hostname_in_domain(bad, domain))
        self.assertTrue(record.hostname_in_domain(good, domain))

    def test_cname_validation_fail(self):
        record = Record()
        record.type = 'C'
        record.domain_id = 1
        record.host = 'foobar.com'
        record.val = 'www.example.com  '

        with self.assertRaises(RecordValueException) as cm:
            record.validate()
        self.assertEquals(
            'Invalid cname value: www.example.com  ',
            str(cm.exception)
        )

    def test_cname_validation_success(self):
        record = Record()
        record.type = 'C'
        record.domain_id = 1
        record.host = 'foobar.com'
        record.val = 'www.example.com'

        self.assertIsNone(record.validate())
