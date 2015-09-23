import unittest

from vegadns.api.models.domain import Record


class TestRecord(unittest.TestCase):
    def test_hostname_in_domain(self):
        record = Record()

        domain = "foobar.com"
        bad = "wwwfoobar.com"
        good = "www.foobar.com"

        self.assertTrue(record.hostname_in_domain(domain, domain))
        self.assertFalse(record.hostname_in_domain(bad, domain))
        self.assertTrue(record.hostname_in_domain(good, domain))
