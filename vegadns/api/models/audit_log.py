from builtins import object
from peewee import CharField, IntegerField, PrimaryKeyField

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class AuditLog(BaseModel):
    log_id = PrimaryKeyField()
    email = CharField(db_column='Email')
    name = CharField(db_column='Name')
    account_id = IntegerField(db_column='cid')
    domain_id = IntegerField(db_column='domain_id')
    entry = CharField()
    time = IntegerField()

    def validate(self):
        if not Validate().email(self.email):
            raise Exception("Invalid email")
        if not self.time:
            raise Exception("time is not set")
        if not self.entry:
            raise Exception("entry is not set")
        if not self.account_id:
            raise Exception("account_id is not set")

    class Meta(object):
        db_table = 'log'
