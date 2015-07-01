import unittest

from vegadns.api.models.recordtypes import RecordType, RecordTypeException


class TestRecordTypes(unittest.TestCase):
    def test_get_success(self):
        record_type = RecordType()
        self.assertEquals(record_type.get('S'), 'SOA')
        self.assertEquals(record_type.get('N'), 'NS')
        self.assertEquals(record_type.get('A'), 'A')
        self.assertEquals(record_type.get('3'), 'AAAA')
        self.assertEquals(record_type.get('6'), 'AAAA+PTR')
        self.assertEquals(record_type.get('M'), 'MX')
        self.assertEquals(record_type.get('P'), 'PTR')
        self.assertEquals(record_type.get('T'), 'TXT')
        self.assertEquals(record_type.get('C'), 'CNAME')
        self.assertEquals(record_type.get('V'), 'SRV')
        self.assertEquals(record_type.get('F'), 'SPF')

    def test_get_failure(self):
        record_type = RecordType()

        with self.assertRaises(RecordTypeException) as cm:
            record_type.get('nonexistant')
        self.assertEquals('Invalid record type', cm.exception.message)

    def test_set_success(self):
        record_type = RecordType()
        self.assertEquals(record_type.set('SOA'), 'S')
        self.assertEquals(record_type.set('NS'), 'N')
        self.assertEquals(record_type.set('A'), 'A')
        self.assertEquals(record_type.set('AAAA'), '3')
        self.assertEquals(record_type.set('AAAA+PTR'), '6')
        self.assertEquals(record_type.set('MX'), 'M')
        self.assertEquals(record_type.set('PTR'), 'P')
        self.assertEquals(record_type.set('TXT'), 'T')
        self.assertEquals(record_type.set('CNAME'), 'C')
        self.assertEquals(record_type.set('SRV'), 'V')
        self.assertEquals(record_type.set('SPF'), 'F')

    def test_set_failure(self):
        record_type = RecordType()

        with self.assertRaises(RecordTypeException) as cm:
            record_type.get('CNAME')
        self.assertEquals('Invalid record type', cm.exception.message)
