from builtins import object
from peewee import AutoField, CharField

from vegadns.api.models import BaseModel


class Group(BaseModel):
    group_id = AutoField()
    name = CharField(unique=True)

    def validate(self):
        if len(self.name) is 0:
            raise ValueError("name must not be empty")

    class Meta(object):
        table_name = 'groups'
