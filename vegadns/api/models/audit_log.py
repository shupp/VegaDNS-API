from peewee import CharField, IntegerField

from vegadns.api.models import database, BaseModel


class AuditLog(BaseModel):
    email = CharField(db_column='Email')
    name = CharField(db_column='Name')
    cid = IntegerField()
    domain_id = IntegerField(db_column='domain_id')
    entry = CharField()
    time = IntegerField()

    class Meta:
        db_table = 'log'
