from builtins import object
from peewee import CharField, IntegerField, AutoField

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class AuditLog(BaseModel):
    log_id = AutoField()
    email = CharField(column_name='Email')
    name = CharField(column_name='Name')
    account_id = IntegerField(column_name='cid')
    domain_id = IntegerField(column_name='domain_id')
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
        table_name = 'log'
