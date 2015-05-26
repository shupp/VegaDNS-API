from peewee import PrimaryKeyField, CharField

from vegadns.api.models import BaseModel


class Group(BaseModel):
    group_id = PrimaryKeyField()
    name = CharField(unique=True)

    def validate(self):
        if len(self.name) is 0:
            raise ValueError("name must not be empty")

    class Meta:
        db_table = 'groups'
