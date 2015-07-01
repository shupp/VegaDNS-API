import re

from peewee import IntegerField, CharField, PrimaryKeyField

from vegadns.api.models import database, BaseModel, ensure_validation
from vegadns.api.models.recordtypes import AbstractRecordType


class Record(BaseModel):
    distance = IntegerField(null=True, default=0)
    domain_id = IntegerField(db_column='domain_id')
    host = CharField()
    port = IntegerField(null=True)
    record_id = PrimaryKeyField()
    ttl = IntegerField()
    type = CharField(null=True)
    val = CharField(null=True)
    weight = IntegerField(null=True)

    def to_recordtype(self):
        instance = AbstractRecordType.singleton(self)
        instance.from_model(self)
        return instance

    class Meta:
        db_table = 'records'

    def validate(self):
        recordtype = self.to_recordtype()
        recordtype.validate()

    @staticmethod
    def hostname_in_domain(hostname, domain):
        p = re.compile(".*" + domain + "([.])?$", re.IGNORECASE)
        m = p.match(hostname)
        return bool(m)
