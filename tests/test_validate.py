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
        self.assertTrue(self.validate.ipv6('FE80::202:B3FF:FE1E:8329'))
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

    def test_is_uuid_valid(self):
        s = '465aba85-7c4b-4631-86c4-ef3404a463f6'
        self.assertTrue(self.validate.uuid(s))

    def test_is_uuid_invalid(self):
        self.assertFalse(self.validate.uuid('foo'))

    def test_ipv4_prefix_valid(self):
        self.assertTrue(self.validate.ip_prefix('127.0.0', 'ipv4'))
        self.assertTrue(self.validate.ip_prefix('255.255.255', 'ipv4'))
        self.assertTrue(self.validate.ip_prefix('1.2', 'ipv4'))
        self.assertTrue(self.validate.ip_prefix('1', 'ipv4'))

    def test_ipv4_prefix_invalid(self):
        self.assertFalse(self.validate.ip_prefix(None, 'ipv4'))
        self.assertFalse(self.validate.ip_prefix('256.0.0', 'ipv4'))
        self.assertFalse(self.validate.ip_prefix('255.255.255.', 'ipv4'))
        self.assertFalse(self.validate.ip_prefix('-25.240.10', 'ipv4'))
        self.assertFalse(self.validate.ip_prefix('', 'ipv4'))

    def test_ipv6_prefix_valid(self):
        self.assertTrue(
            self.validate.ip_prefix('FE80:0000:0000:0000:0202:B3FF', 'ipv6')
        )
        self.assertTrue(
            self.validate.ip_prefix('FE80:0202:B3FF:FE1E:8329', 'ipv6')
        )
        self.assertTrue(self.validate.ip_prefix('FE80', 'ipv6'))

    def test_ipv6_prefix_invalid(self):
        self.assertFalse(self.validate.ip_prefix(None, 'ipv6'))
        self.assertFalse(
            self.validate.ip_prefix('FE80:0000:0000:0000:0202:B3FG', 'ipv6')
        )
        self.assertFalse(
            self.validate.ip_prefix('FE80:202:B3FF:FE1E:8329', 'ipv6')
        )
        self.assertFalse(self.validate.ip_prefix(
            'FE80:0000:0000:0000:0202:B3FF:0000:0000:0000:0000', 'ipv6')
        )

    def test_email_valid(self):
        self.assertTrue(self.validate.email('user@example.com'))
        self.assertFalse(self.validate.email('example.com'))
