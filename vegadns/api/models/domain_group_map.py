from peewee import PrimaryKeyField, CharField, IntegerField

from vegadns.api.models import database, BaseModel


class DomainGroupMap(BaseModel):
    map_id = PrimaryKeyField()
    group_id = IntegerField()
    domain_id = IntegerField()
    permissions = IntegerField(default=3)

    class Meta:
        db_table = 'domain_group_map'
        indexes = (
            (('domain_id', 'group_id'), True),
        )

    READ_PERM = 1
    WRITE_PERM = 2
    DELETE_PERM = 4

    def __init__(self, *args, **kwargs):
        super(DomainGroupMap, self).__init__(args, kwargs)
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
        my_dict['can_read'] = self.has_perm(self.READ_PERM)
        my_dict['can_write'] = self.has_perm(self.WRITE_PERM)
        my_dict['can_delete'] = self.has_perm(self.DELETE_PERM)

        return my_dict
