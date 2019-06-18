from builtins import object
import logging
from peewee import Model
from playhouse.shortcuts import model_to_dict

from vegadns.api.db import database


logger = logging.getLogger(__name__)


def ensure_validation(func):
    def run_validation(self, *args, **kwargs):
        self.validate()
        return func(self, *args, **kwargs)
    return run_validation


class BaseModel(Model):
    def to_dict(self):
        return model_to_dict(self)

    def to_clean_dict(self):
        unclean_dict = self.to_dict()
        if hasattr(self, "clean_keys"):
            for key in self.clean_keys:
                unclean_dict.pop(key, None)

        return unclean_dict

    @ensure_validation
    def save(self, *args, **kwargs):
        # print self
        super(BaseModel, self).save(*args, **kwargs)

    @ensure_validation
    def create(self, *args, **kwargs):
        super(BaseModel, self).create(*args, **kwargs)

    def validate(self):
        raise Exception('No validation defined')

    class Meta(object):
        database = database
