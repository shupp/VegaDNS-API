import unittest

from vegadns.validate import Validate


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.validate = Validate()

    def test_ipv4_valid(self):
        self.assertTrue(self.validate.ipv4('127.0.0.1'))
        self.assertTrue(self.validate.ipv4('255.255.255.0'))
        self.assertTrue(self.validate.ipv4('1.2.3.4'))

    def test_ipv4_invalid(self):
        self.assertFalse(self.validate.ipv4('4'))
        self.assertFalse(self.validate.ipv4('4.2.3'))
        self.assertFalse(self.validate.ipv4('294.1.2.0'))
        self.assertFalse(self.validate.ipv4('255.255.255.256'))
        self.assertFalse(self.validate.ipv4('fe80::1610:9fff:fee3:74a9%en0'))
        self.assertFalse(self.validate.ipv4('i like turtles'))

    def test_ipv6_valid(self):
        self.assertTrue(
            self.validate.ipv6('FE80:0000:0000:0000:0202:B3FF:FE1E:8329')
        )
        self.assertTrue(self.validate.ipv6('FE80::0202:B3FF:FE1E:8329'))
        self.assertTrue(self.validate.ipv6('fe80::1'))

    def test_ipv6_invalid(self):
        self.assertFalse(self.validate.ipv6('4'))
        self.assertFalse(self.validate.ipv6('4.2.3'))
        self.assertFalse(self.validate.ipv6('294.1.2.0'))
        self.assertFalse(self.validate.ipv6('255.255.255.256'))
        self.assertFalse(self.validate.ipv6('i like turtles'))

    def test_record_name_valid(self):
        self.assertTrue(self.validate.record_hostname('vegadns.org'))
        self.assertTrue(self.validate.record_hostname('www.vegadns.org'))
        self.assertTrue(self.validate.record_hostname('foo.www.vegadns.org'))
        self.assertTrue(self.validate.record_hostname('b.foo.www.vegadns.org'))

        self.assertTrue(
            self.validate.record_hostname('foo-bar.foo.www.vegadns.org')
        )

    def test_record_name_invalid(self):
        self.assertFalse(self.validate.record_hostname('foo'))
        self.assertFalse(self.validate.record_hostname('..vegadns.org'))

    def test_is_sha256_valid(self):
        s = 'c69c30d355dd7c8ab3ecae9c005701a51d30e7c3af1855f1f1be3c7919b2b2c1'
        self.assertTrue(self.validate.sha256(s))

    def test_is_sha256_invalid(self):
        self.assertFalse(self.validate.sha256('foo'))

        s = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
        self.assertFalse(self.validate.sha256(s))

        s = 'e7c3af1855f1f1be3c7919b2b2c1'
        self.assertFalse(self.validate.sha256(s))
