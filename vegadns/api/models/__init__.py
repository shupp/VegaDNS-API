# need logger
from vegadns.api.config import config
from peewee import *
from lib.shortcuts import model_to_dict


database = MySQLDatabase(
    config.get('mysql', 'database'),
    **{
        'host': config.get('mysql', 'host'),
        'password': config.get('mysql', 'password'),
        'user': config.get('mysql', 'user')
      }
)


def ensure_validation(func):
    def run_validation(self, *args, **kwargs):
        self.validate()
        return func(self, *args, **kwargs)
    return run_validation


class BaseModel(Model):
    def to_dict(self):
        return model_to_dict(self)

    @ensure_validation
    def save(self, *args, **kwargs):
        # print self
        super(BaseModel, self).save(*args, **kwargs)

    @ensure_validation
    def create(self, *args, **kwargs):
        super(BaseModel, self).create(*args, **kwargs)

    def validate(self):
        raise Exception('No validation defined')

    class Meta:
        database = database
