from peewee import CharField, IntegerField

from vegadns.api.models import database, BaseModel


class DefaultRecord(BaseModel):
    default_type = CharField()
    distance = IntegerField(null=True)
    group_owner_id = IntegerField(db_column='group_owner_id', null=True)
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
        db_table = 'default_records'
