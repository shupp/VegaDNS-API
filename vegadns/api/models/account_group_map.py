from peewee import PrimaryKeyField, IntegerField

from vegadns.api.models import BaseModel


class AccountGroupMap(BaseModel):
    map_id = PrimaryKeyField()
    account_id = IntegerField()
    group_id = IntegerField()
    is_admin = IntegerField(default=0)

    class Meta:
        db_table = 'account_group_map'
        indexes = (
            (('account_id', 'group_id'), True),
        )
