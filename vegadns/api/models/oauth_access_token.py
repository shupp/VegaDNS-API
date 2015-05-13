from peewee import PrimaryKeyField, IntegerField, CharField

from vegadns.api.models import database, BaseModel
from vegadns.validate import Validate


class OauthAccessToken(BaseModel):
    access_token_id = PrimaryKeyField()
    account_id = IntegerField(null=False)
    apikey_id = IntegerField()
    access_token = CharField(max_length=36, null=False, unique=True)
    grant_type = CharField(
        max_length=20,
        null=False,
        default='client_credentials'
    )
    expires_at = IntegerField(default=0)

    def validate(self):
        v = Validate()
        if not v.uuid(self.access_token):
            raise Exception('Invalid access_token')

    class Meta:
        db_table = 'oauth_access_tokens'
