from peewee import *
from vegadns.api.models import database, BaseModel


class Record(BaseModel):
    distance = IntegerField(null=True)
    domain_id = IntegerField(db_column='domain_id')
    host = CharField()
    port = IntegerField(null=True)
    record_id = IntegerField(
        db_column='record_id',
        unique=True,
        primary_key=True
    )
    ttl = IntegerField()
    type = CharField(null=True)
    val = CharField(null=True)
    weight = IntegerField(null=True)

    class Meta:
        db_table = 'records'


class RecordTypeException(Exception):
    pass


class RecordType(object):
    record_types = {
        'S': 'SOA',
        'N': 'NS',
        'A': 'A',
        '3': 'AAAA',
        '6': 'AAAA+PTR',
        'M': 'MX',
        'P': 'PTR',
        'T': 'TXT',
        'C': 'CNAME',
        'V': 'SRV',
        'F': 'SPF'
    }

    def get(self, type):
        if type in self.record_types.keys():
            return self.record_types[type]
        else:
            raise RecordTypeException('Invalid record type')

    def set(self, type):
        reversed = {v: k for k, v in self.record_types.items()}

        if type in reversed:
            return reversed[type]
        else:
            raise RecordTypeException('Invalid record type')
