from peewee import CharField, IntegerField

from vegadns.api.models import database, BaseModel


class Domain(BaseModel):
    domain = CharField()
    domain_id = IntegerField(primary_key=True)
    group_owner_id = IntegerField(db_column='group_owner_id', null=True)
    owner_id = IntegerField(db_column='owner_id', null=True)
    status = CharField()

    class Meta:
        db_table = 'domains'

    # For removing unused group_owner field via self.to_clean_dict()
    clean_keys = ["group_owner_id"]
