from builtins import object
from peewee import CharField, IntegerField, PrimaryKeyField, DoesNotExist

from vegadns.api.models import database, BaseModel
from vegadns.api.models.record import Record
from vegadns.api.models.default_record import DefaultRecord
from vegadns.api.models.recordtypes import RecordType
from vegadns.api.models.domain_group_map import DomainGroupMap
from vegadns.validate.dns import ValidateDNS


class Domain(BaseModel):
    domain = CharField(unique=True)
    domain_id = PrimaryKeyField()
    group_owner_id = IntegerField(
        db_column='group_owner_id', null=True, default=0
    )
    owner_id = IntegerField(db_column='owner_id', null=True, default=0)
    status = CharField(default="active")

    class Meta(object):
        db_table = 'domains'

    # For removing unused group_owner field via self.to_clean_dict()
    clean_keys = ["group_owner_id"]

    def validate(self):
        if self.status not in ["active", "inactive"]:
            raise ValueError("status must be either 'active' or 'inactive'")

        if not ValidateDNS.record_hostname(self.domain):
            raise ValueError("domain is invalid: " + self.domain)

    def get_records(self):
        if not self.domain_id:
            raise Exception("Cannot get records, domain_id is not set")

        return Record.select(Record).where(
            Record.domain_id == self.domain_id
        )

    def count_records(
        self, filter_record_type, search_name=None, search_value=None
    ):
        if not self.domain_id:
            raise Exception("Cannot get records, domain_id is not set")

        query = Record.select(Record).where(Record.domain_id == self.domain_id)
        if filter_record_type is not None:
            query = query.where(
                Record.type == RecordType().set(filter_record_type)
            )

        if search_name is not None:
            query = query.where(
                (Record.host ** ('%' + search_name + '%'))
            )

        if search_value is not None:
            query = query.where(
                (Record.val ** ('%' + search_value + '%'))
            )

        return query.count()

    def add_default_soa_record(self, endpoint=None):
        """Returns None if already exists, DoesNotExist bubbles up when no
        default soa exists"""

        # sanity check
        if not self.domain_id:
            raise Exception(
                "Cannot add default records when domain_id is not set"
            )

        # don't duplicate SOA record
        try:
            existing_soa = Record.get(
                Record.domain_id == self.domain_id,
                Record.type == RecordType().set("SOA")
            )
            return None
        except DoesNotExist:
            # create SOA record, let DoesNotExist bubble up
            default_soa = DefaultRecord.get(
                DefaultRecord.type == RecordType().set("SOA")
            )
            soa = Record()
            soa.domain_id = self.domain_id
            soa.host = default_soa.host.replace("DOMAIN", self.domain)
            soa.val = default_soa.val
            soa.ttl = default_soa.ttl
            soa.type = default_soa.type

            # replace uses of DOMAIN
            soa.save()
            if endpoint is not None:
                endpoint.dns_log(soa.domain_id, "added soa")

            return soa

    def add_default_records(self, endpoint=None, skipSoa=False):
        # sanity check
        if not self.domain_id:
            raise Exception(
                "Cannot add default records when domain_id is not set"
            )

        if not skipSoa:
            try:
                soa = self.add_default_soa_record(endpoint)
            except DoesNotExist:
                # no default SOA record set!
                pass

        # create all other records
        default_records = DefaultRecord.select().where(
            DefaultRecord.type != RecordType().set("SOA")
        )

        for record in default_records:
            new = Record()

            new.domain_id = self.domain_id
            new.distance = record.distance
            new.host = record.host.replace("DOMAIN", self.domain)
            new.val = record.val.replace("DOMAIN", self.domain)
            new.distance = record.distance
            new.port = record.port
            new.ttl = record.ttl
            new.type = record.type
            new.weight = record.weight

            new.save()
            if endpoint is not None:
                endpoint.dns_log(
                    new.domain_id,
                    (
                        "added " + RecordType().get(new.type) +
                        " with host " + new.host +
                        " and value " + new.val
                    )
                )

    def get_domain_group_maps(self):
        if not self.domain_id:
            raise Exception("Cannot get maps, domain_id is not set")

        return DomainGroupMap.select(DomainGroupMap).where(
            DomainGroupMap.domain_id == self.domain_id
        )

    def delete_records(self):
        for record in self.get_records():
            record.delete_instance()

    def delete_domain_group_maps(self):
        for map in self.get_domain_group_maps():
            map.delete_instance()
