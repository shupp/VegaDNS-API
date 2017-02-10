import logging

import redis

from vegadns.api.config import config


logger = logging.getLogger(__name__)


class Notifier(object):
    def send(self):
        redis_enabled = config.get(
            'update_notifications',
            'enable_redis_notifications'
        )

        if redis_enabled in ["True", "true"]:
            redis_host = config.get('update_notifications', 'redis_host')
            redis_port = config.get('update_notifications', 'redis_port')
            redis_channel = config.get('update_notifications', 'redis_channel')

            try:
                r = redis.Redis(host=redis_host, port=redis_port)
                r.publish(redis_channel, "UPDATE")
            except Exception as e:
                logger.critical(e)
