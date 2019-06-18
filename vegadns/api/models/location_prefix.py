from builtins import object
from peewee import CharField, AutoField, IntegerField

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class LocationPrefix(BaseModel):
    prefix_id = AutoField()
    location_id = IntegerField()
    prefix = CharField(unique=True)
    prefix_type = CharField(default='ipv4')
    prefix_description = CharField()

    class Meta(object):
        table_name = 'location_prefixes'

    def validate(self):
        if self.prefix_type not in ['ipv4', 'ipv6']:
            raise ValueError("prefix_type must be ipv4 or ipv6")

        if not Validate().ip_prefix(self.prefix, self.prefix_type):
            raise ValueError("prefix must be a valid network prefix")

        if self.location_id is None:
            raise ValueError("location_id is required")
