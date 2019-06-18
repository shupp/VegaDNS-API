from builtins import str
from builtins import object
import hashlib
import bcrypt
import re

from peewee import CharField, IntegerField, PrimaryKeyField, DoesNotExist

from vegadns.api.config import config
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

    class Meta(object):
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

        if self.status not in ["active", "inactive"]:
            raise Exception("Invalid status: " + self.status)

    def get_password_algo(self):
        exploded = self.password.split("|")
        if len(exploded) == 1:
            return "md5"

        # format: algo|salt|hash
        # e.g. bcrypt||hash_which_includes_salt
        if len(exploded) == 3:
            return exploded[0]

    def get_password_hash(self):
        exploded = self.password.split("|")
        if len(exploded) < 3:
            return exploded[0]

        return exploded[2]

    def check_password(self, clear_text):
        if self.get_password_algo() == "md5":
            return self.check_password_md5(clear_text)
        else:
            # just bcrypt for now
            return self.check_password_bcrypt(clear_text)

    def check_password_md5(self, clear_text):
        return self.get_password_hash() == hashlib.md5(clear_text.encode('utf-8')).hexdigest()

    def check_password_bcrypt(self, clear_text):
        hashed = self.get_password_hash()
        return bcrypt.checkpw(
            clear_text.encode('utf-8'),
            hashed.encode('utf-8')
        )

    def set_password(self, clear_text):
        # use bcrypt
        hashed = bcrypt.hashpw(clear_text.encode('utf-8'), bcrypt.gensalt())
        self.password = "bcrypt||".encode('utf-8') + hashed

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
        if group_ids:
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
                self.domains[domain.domain_id] = {
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
        # FIXME - type juggling should happen at endpoints
        domain_id = int(domain_id)
        if domain_id not in list(self.domains.keys()):
            return False
        if self.domains[domain_id]["domain"].owner_id == self.account_id:
            return True
        for map in self.domains[domain_id]["maps"]:
            if map.has_perm(permission):
                return True

        return False

    def generate_cookie_value(self, account, agent):
        cookie_secret = config.get("auth", "cookie_secret")
        account_id = str(account.account_id)
        string = (account_id + str(account.password) + cookie_secret + agent)
        hash = hashlib.md5(string.encode('utf-8')).hexdigest()

        return account_id + "-" + hash

    def in_global_acl_emails(self, email):
        # load emails and verify
        emails = [
            x.strip() for x in config.get(
                "global_record_acls", "acl_emails"
            ).strip('"').split(",")
        ]
        if email in emails:
            return True

        return False

    def get_global_acl_labels(self):
        config_labels = config.get(
            "global_record_acls",
            "acl_labels"
        ).strip('"')
        if len(config_labels) == 0:
            return []

        return [x.strip() for x in config_labels.split(",")]

    def get_domain_by_record_acl(self, domain_id, record_name, record_type):
        if str(record_type).upper() == "SOA":
            # SOA records are not allowed
            return False

        if not self.in_global_acl_emails(self.email):
            return False

        labels = self.get_global_acl_labels()

        # load domain
        domain = self.get_domain_object().get(Domain.domain_id == domain_id)

        # check no sublabel use case (DOMAIN)
        # i.e. example.com for domain example.com
        if record_name == domain.domain and 'DOMAIN' in labels:
            return domain

        # check single sublabel match
        # i.e. _acme-challenge.example.com for domain example.com
        pattern = "\." + domain.domain + "$"
        sublabel = re.sub(pattern, "", record_name)
        if sublabel in labels:
            return domain

        # dummy check that the record_name ends with the correct domain
        if not record_name.endswith(domain.domain):
            return False

        # If no match, then check for multiple labels in the sublabel
        # i.e. _acme-challenge.office.example.com for domain example.com
        sublabels = sublabel.split(".")
        if len(sublabels) is 1:
            # Only one sublabel, so no match
            return False
        if sublabels[0] not in labels:
            # First sublabel isn't allowed
            return False

        # Now let's make sure there isn't a domain collision
        # Pop off first sublabel
        sublabels.pop(0)
        while len(sublabels) >= 1:
            try:
                d = self.get_domain_object().get(
                    Domain.domain == '.'.join(sublabels) + '.' + domain.domain
                )
                if d.domain_id == domain.domain_id:
                    # Should not get here, but just in case
                    # domain name and id match, done checking
                    return domain
                else:
                    # collision!
                    return False
            except DoesNotExist:
                sublabels.pop(0)
                if len(sublabels) is 0:
                    # Done checking, no collisions
                    return domain
                else:
                    # no collisions yet, keep checking
                    continue

        # Should not ever get here, but just in case
        return False

    def get_domain_object(self):
        return Domain
