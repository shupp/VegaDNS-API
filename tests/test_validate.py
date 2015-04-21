import unittest

from vegadns.validate.records import Validate


class TestValidate(unittest.TestCase):
    def test_ipv4_valid(self):
        self.assertTrue(Validate.ipv4('127.0.0.1'))
        self.assertTrue(Validate.ipv4('255.255.255.0'))
        self.assertTrue(Validate.ipv4('1.2.3.4'))

    def test_ipv4_invalid(self):
        self.assertFalse(Validate.ipv4('4'))
        self.assertFalse(Validate.ipv4('4.2.3'))
        self.assertFalse(Validate.ipv4('294.1.2.0'))
        self.assertFalse(Validate.ipv4('255.255.255.256'))
        self.assertFalse(Validate.ipv4('fe80::1610:9fff:fee3:74a9%en0'))
        self.assertFalse(Validate.ipv4('i like turtles'))

    def test_ipv6_valid(self):
        self.assertTrue(
            Validate.ipv6('FE80:0000:0000:0000:0202:B3FF:FE1E:8329')
        )
        self.assertTrue(Validate.ipv6('FE80::0202:B3FF:FE1E:8329'))
        self.assertTrue(Validate.ipv6('fe80::1'))

    def test_ipv6_invalid(self):
        self.assertFalse(Validate.ipv6('4'))
        self.assertFalse(Validate.ipv6('4.2.3'))
        self.assertFalse(Validate.ipv6('294.1.2.0'))
        self.assertFalse(Validate.ipv6('255.255.255.256'))
        self.assertFalse(Validate.ipv6('i like turtles'))

    def test_record_name_valid(self):
        self.assertTrue(Validate.record_hostname('www.vegadns.org'))
        self.assertTrue(Validate.record_hostname('foo.www.vegadns.org'))
        self.assertTrue(Validate.record_hostname('bar.foo.www.vegadns.org'))

        self.assertTrue(
            Validate.record_hostname('foo-bar.foo.www.vegadns.org')
        )
        self.assertTrue(
            Validate.record_hostname('1.0/24.1.168.192.in-addr.arpa')
        )

    def test_record_name_invalid(self):
        self.assertFalse(Validate.record_hostname('foo'))
        self.assertFalse(Validate.record_hostname('..vegadns.org'))
