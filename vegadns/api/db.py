import logging

from vegadns.api.config import config
from peewee import MySQLDatabase

logger = logging.getLogger(__name__)


database = MySQLDatabase(
    config.get('mysql', 'database'),
    **{
        'host': config.get('mysql', 'host'),
        'password': config.get('mysql', 'password'),
        'user': config.get('mysql', 'user'),
        'ssl': {'ca': v for k, v in config.items('mysql') if k == 'ssl_ca'}
      }
)
