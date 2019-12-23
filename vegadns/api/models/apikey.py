from builtins import str
from builtins import object
from peewee import AutoField, IntegerField, CharField

import hmac
import hashlib
import time
import random

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class ApiKey(BaseModel):
    apikey_id = AutoField()
    account_id = IntegerField(null=False, default=0)
    description = CharField()
    key = CharField(null=False, default='', unique=True)
    secret = CharField(null=False, default='')
    date_created = IntegerField(default=int(time.time()))
    deleted = IntegerField(default=0)

    def generate(self):
        self.key = self.create_string()
        self.secret = self.create_string()

    def create_string(self):
        key = str(time.time() + random.randint(1, 1000)).encode('utf-8')
        data = str(time.time() + random.randint(1, 1000)).encode('utf-8')
        return hmac.new(bytes(key), bytes(data), hashlib.sha256).hexdigest()

    def validate(self):
        v = Validate()
        if not v.sha256(self.key):
            raise Exception('Invalid key')
        if not v.sha256(self.secret):
            raise Exception('Invalid secret')
        if self.deleted != 0 and self.deleted != 1:
            raise Exception('deleted must be 1 or 0')

    class Meta(object):
        table_name = 'api_keys'
