import unittest

from mock import MagicMock

from vegadns.api.models.domain import Domain
from vegadns.api.models.record import Record
from vegadns.api.export.tinydns import ExportTinydnsData


class TestTinydnsExport(unittest.TestCase):
    def setUp(self):
        self.export = ExportTinydnsData()
        Record.save = None
        Record.create = None
        Record.delete = None

    def test_a_record(self):
        model = Record()

        model.type = 'A'
        model.host = 'foo.vegadns.ubuntu'
        model.val = '1.2.3.4'
        model.ttl = '3600'

        self.assertEquals(
            self.export.data_line_from_model(model),
            '+foo.vegadns.ubuntu:1.2.3.4:3600\n'
        )

    def test_mx_record(self):
        model = Record()

        model.type = 'M'
        model.host = 'vegadns.ubuntu'
        model.val = 'mail.vegadns.ubuntu'
        model.distance = 10
        model.ttl = '3600'

        self.assertEquals(
            self.export.data_line_from_model(model),
            '@vegadns.ubuntu::mail.vegadns.ubuntu:10:3600\n'
        )

    def test_mx_record(self):
        model = Record()

        model.type = 'P'
        model.host = '4.3.2.1.in-addr.arpa'
        model.val = 'www.vegadns.ubuntu'
        model.ttl = '3600'

        self.assertEquals(
            self.export.data_line_from_model(model),
            '^4.3.2.1.in-addr.arpa:www.vegadns.ubuntu:3600\n'
        )

    def test_ptr_record(self):
        model = Record()

        model.type = 'T'
        model.host = 'vegadns.ubuntu'
        model.val = 'v=spf1 mx a ip4:1.2.3.0/24'
        model.ttl = '3600'

        self.assertEquals(
            self.export.data_line_from_model(model),
            "'vegadns.ubuntu:v=spf1 mx a ip4" r"\072" + "1.2.3.0/24:3600\n"
        )

    def test_spf_record(self):
        model = Record()

        model.type = 'F'
        model.host = 'example.com'
        model.val = 'v=spf1 mx -all'
        model.ttl = '3600'

        self.assertEquals(
            self.export.data_line_from_model(model),
            ":example.com:99:" r"\016" "v=spf1 mx -all:3600\n"
        )

    def test_aaaa_record(self):
        model = Record()

        model.type = '3'
        model.host = 'example.com'
        model.val = '0000:0000:0000:0000:0000:ffff:169.254.123.231'
        model.ttl = '3600'

        expected = (
            ":example.com:28:"
            r"\000\000\000\000\000\000\000\000\000\000\377\377\251\376\173\347"
            ":3600\n"
        )

        self.assertEquals(
            self.export.data_line_from_model(model),
            expected
        )

    def test_aaaaptr_record(self):
        model = Record()

        model.type = '3'
        model.host = 'example.com'
        model.val = '0000:0000:0000:0000:0000:ffff:169.254.123.231'
        model.ttl = '3600'

        expected = (
            ":example.com:28:"
            r"\000\000\000\000\000\000\000\000\000\000\377\377\251\376\173\347"
            ":3600\n"
        )

        self.assertEquals(
            self.export.data_line_from_model(model),
            expected
        )

    def test_aaaaptr_record(self):
        model = Record()

        model.type = '6'
        model.host = 'example.com'
        model.val = '0000:0000:0000:0000:0000:ffff:169.254.123.231'
        model.ttl = '3600'

        expected = (
            ":example.com:28:"
            r"\000\000\000\000\000\000\000\000\000\000\377\377\251\376\173\347"
            ":3600\n"

            "^7.e.b.7.e.f.9.a.f.f.f.f.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"
            ".ip6.arpa"
            ":example.com:3600\n"
        )

        self.assertEquals(
            self.export.data_line_from_model(model),
            expected
        )

    def test_soa_record(self):
        domain = Domain()
        domain.domain = 'example.com'
        model = Record()

        # joined domain on domain_id
        model.domain_id = domain
        model.type = 'S'
        model.host = 'hostmaster.example.com:ns1.example.com'
        model.val = '16384:2048:1048576:2560:'
        model.ttl = '86400'

        expected = (
            "Zexample.com"
            ":ns1.example.com"
            ":hostmaster.example.com"
            ":"
            ":16384"
            ":2048"
            ":1048576"
            ":2560"
            ":86400\n"
        )

        self.assertEquals(
            self.export.data_line_from_model(model),
            expected
        )

    def test_srv_record(self):
        model = Record()

        model.type = 'V'
        model.host = '_xmpp-client._tcp.example.com.'
        model.val = 'xmpp.example.com'
        model.ttl = '3600'
        model.distance = 0
        model.weight = 10
        model.port = 5222

        expected = (
            ":_xmpp-client._tcp.example.com."
            ":33"
            r":\000\000\000\012\024\146\004xmpp\007example\003com\000"
            ":3600\n"
        )

        self.assertEquals(
            self.export.data_line_from_model(model),
            expected
        )
