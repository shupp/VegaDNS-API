from peewee import PrimaryKeyField, IntegerField

from vegadns.api.models import BaseModel


class AccountGroupMap(BaseModel):
    map_id = PrimaryKeyField()
    account_id = IntegerField()
    group_id = IntegerField()
    is_admin = IntegerField(default=0)

    def validate(self):
        if self.is_admin != 0 and self.is_admin != 1:
            raise ValueError("is_admin must be 1 or 0")

    # helper method for formatting API output
    def format_member(self, map, account):
        return {
            'member_id': map.map_id,
            'group_id': map.group_id,
            'is_admin': map.is_admin,
            'account': account.to_clean_dict()
        }

    class Meta:
        db_table = 'account_group_map'
        indexes = (
            (('account_id', 'group_id'), True),
        )
