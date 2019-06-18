from builtins import str
from builtins import object
import hmac
import hashlib
import time
import random

from peewee import CharField, IntegerField, AutoField

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class PasswordResetToken(BaseModel):
    token_id = AutoField()
    account_id = IntegerField()
    token_value = CharField(unique=True)
    date_created = IntegerField()

    EXPIRE_IN = 1800

    # For removing account and expire info from self.to_clean_dict()
    clean_keys = ["account_id", "date_created"]

    def validate(self):
        if not Validate().sha256(self.token_value):
            raise Exception("Invalid email")
        if not self.date_created:
            raise Exception("date_created is not set")
        if not self.account_id:
            raise Exception("account_id is not set")

    class Meta(object):
        table_name = 'password_reset_tokens'

    def generateToken(self):
        key = time.time() + random.randint(1, 1000)
        data = time.time() + random.randint(1, 10000)
        return hmac.new(str(key), str(data), hashlib.sha256).hexdigest()
