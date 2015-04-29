from peewee import *

from vegadns.api.models import database, BaseModel


class Account(BaseModel):
    account_type = CharField(db_column='Account_Type')
    email = CharField(db_column='Email', unique=True)
    first_name = CharField(db_column='First_Name')
    last_name = CharField(db_column='Last_Name')
    password = CharField(db_column='Password')
    phone = CharField(db_column='Phone')
    status = CharField(db_column='Status')
    cid = IntegerField(primary_key=True)
    gid = IntegerField(null=True)

    class Meta:
        db_table = 'accounts'
