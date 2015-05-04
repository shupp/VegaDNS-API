import unittest

from mock import MagicMock

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
