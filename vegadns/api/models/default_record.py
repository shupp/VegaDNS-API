from builtins import object
from peewee import CharField, IntegerField, PrimaryKeyField

from vegadns.api.models import database, BaseModel
import vegadns.api.models.recordtypes


class DefaultRecord(BaseModel):
    default_type = CharField()
    distance = IntegerField(null=True)
    group_owner_id = IntegerField(db_column='group_owner_id', null=True)
    host = CharField()
    port = IntegerField(null=True)
    record_id = PrimaryKeyField(db_column='record_id')
    ttl = IntegerField()
    type = CharField(null=True)
    val = CharField(null=True)
    weight = IntegerField(null=True)

    def to_recordtype(self):
        instance = vegadns.api.models.recordtypes.AbstractRecordType.singleton(
            self
        )
        instance.from_model(self)
        return instance

    class Meta(object):
        db_table = 'default_records'

    def validate(self):
        recordtype = self.to_recordtype()
        recordtype.validate(default_record=True)
