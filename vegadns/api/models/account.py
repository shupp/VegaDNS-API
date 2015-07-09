import hashlib

from peewee import CharField, IntegerField, PrimaryKeyField

from vegadns.api.models import database, BaseModel
from vegadns.api.models.domain import Domain
from vegadns.api.models.account_group_map import AccountGroupMap
from vegadns.api.models.domain_group_map import DomainGroupMap
from vegadns.validate import Validate


class Account(BaseModel):
    account_type = CharField(db_column='Account_Type')
    email = CharField(db_column='Email', unique=True)
    first_name = CharField(db_column='First_Name')
    last_name = CharField(db_column='Last_Name')
    password = CharField(db_column='Password')
    phone = CharField(db_column='Phone')
    status = CharField(db_column='Status')
    account_id = PrimaryKeyField(db_column='cid')
    gid = IntegerField(null=True)

    # For removing password and gid fields via self.to_clean_dict()
    clean_keys = ["gid", "password"]

    class Meta:
        db_table = 'accounts'

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(args, kwargs)
        # a dictionary of domain ids to a list of domain group map permissions
        self.domains = {}

    def validate(self):
        if not Validate().email(self.email):
            raise Exception("Invalid email: " + self.email)

        if not self.first_name:
            raise Exception("first_name must not be empty")

        if not self.last_name:
            raise Exception("last_name must not be empty")

        if self.account_type not in ["senior_admin", "group_admin", "user"]:
            raise Exception("Invalid account_type: " + self.account_type)

        if self.status not in ["active", "active"]:
            raise Exception("Invalid status: " + self.status)

    def set_password(self, clear_text):
        self.password = self.hash_password(clear_text)

    def hash_password(self, clear_text):
        return hashlib.md5(clear_text).hexdigest()

    # helper methods for domain permissions
    def load_domains(self):
        # reset
        self.domains = {}

        # look up my group ids
        accountgroupmaps = AccountGroupMap.select(
            AccountGroupMap.group_id
        ).where(
            AccountGroupMap.account_id == self.account_id
        )
        group_ids = []
        for map in accountgroupmaps:
            group_ids.append(map.group_id)

        # get domain group maps
        domaingroupmaps = DomainGroupMap.select(
            DomainGroupMap, Domain
        ).where(
            DomainGroupMap.group_id << group_ids
        ).join(
            Domain,
            on=Domain.domain_id == DomainGroupMap.domain_id
        )

        # store the maps by domain id for the can_* methods below
        for map in domaingroupmaps:
            did = map.domain_id.domain_id
            if map.domain_id.domain_id not in self.domains:
                self.domains[did] = {
                    'domain': map.domain_id,
                    'maps': []
                }
            self.domains[did]["maps"].append(map)

        # grab domains this user owns
        domains = Domain.select(
            Domain
        ).where(
            Domain.owner_id == self.account_id
        )

        for domain in domains:
            if domain.domain_id not in self.domains:
                self.domains[domain_id] = {
                    'domain': domain,
                    'maps': []
                }

    def can_read_domain(self, domain_id):
        return self.get_domain_permission(
            domain_id,
            DomainGroupMap.READ_PERM
        )

    def can_write_domain(self, domain_id):
        return self.get_domain_permission(
            domain_id,
            DomainGroupMap.WRITE_PERM
        )

    def can_delete_domain(self, domain_id):
        return self.get_domain_permission(
            domain_id,
            DomainGroupMap.DELETE_PERM
        )

    def get_domain_permission(self, domain_id, permission):
        if domain_id not in self.domains:
            return False
        if self.domains[domain_id]["domain"].owner_id == self.account_id:
            return True
        for map in self.domains[domain_id]["maps"]:
            if map.has_perm(permission):
                return True

        return False
