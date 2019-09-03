from builtins import object
from peewee import AutoField, CharField, IntegerField

from vegadns.api.models import database, BaseModel


class DomainGroupMap(BaseModel):
    map_id = AutoField()
    group_id = IntegerField()
    domain_id = IntegerField()
    permissions = IntegerField(default=3)

    class Meta(object):
        table_name = 'domain_group_map'
        indexes = (
            (('domain_id', 'group_id'), True),
        )

    READ_PERM = 1
    WRITE_PERM = 2
    DELETE_PERM = 4

    def __init__(self, *args, **kwargs):
        super(DomainGroupMap, self).__init__(*args, **kwargs)
        self.allowed_perms = [
            self.READ_PERM,
            self.WRITE_PERM,
            self.DELETE_PERM
        ]

    def has_perm(self, perm):
        if perm not in self.allowed_perms:
            raise ValueError(perm + " is not in allowed_perms")

        return bool(self.permissions & perm)

    def set_perm(self, perm, value):
        if perm not in self.allowed_perms:
            raise ValueError(perm + " is not in allowed_perms")

        if bool(value):
            self.permissions = self.permissions | perm
        else:
            self.permissions = self.permissions & ~perm

    def to_dict(self):
        my_dict = super(DomainGroupMap, self).to_dict()
        self.to_readable_permissions(my_dict, self)

        return my_dict

    def to_readable_permissions(self, my_dict, map):
        my_dict["can_read"] = map.has_perm(self.READ_PERM)
        my_dict["can_write"] = map.has_perm(self.WRITE_PERM)
        my_dict["can_delete"] = map.has_perm(self.DELETE_PERM)

    def validate(self):
        total = 0
        for perm in self.allowed_perms:
            total += perm

        if self.permissions < 0 or self.permissions > total:
            raise ValueError("permissions out of range")

    def format_map(self, joined_map):
        new = {}
        new["map_id"] = joined_map.map_id
        new["group"] = joined_map.group_id.to_clean_dict()
        new["domain"] = joined_map.domain_id.to_clean_dict()
        self.to_readable_permissions(new, joined_map)

        return new
