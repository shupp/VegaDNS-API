import logging

import redis
import consul
import uuid

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

        consul_enabled = config.get(
            'update_notifications',
            'enable_consul_notifications'
        )

        if consul_enabled in ["True", "true"]:
            consul_host = config.get('update_notifications', 'consul_host')
            consul_port = config.get('update_notifications', 'consul_port')
            consul_scheme = config.get('update_notifications', 'consul_scheme')
            consul_key = config.get('update_notifications', 'consul_key')
            consul_token = config.get('update_notifications', 'consul_token')
            consul_verify_ssl = config.get(
                'update_notifications', 'consul_verify_ssl'
            )

            # Make sure consul_verify_ssl is type bool
            if (consul_verify_ssl is True or
                    consul_verify_ssl in ["True", "true"]):
                consul_verify_ssl = True
            else:
                consul_verify_ssl = False

            # Make sure consul_token string or None
            if (consul_token is None or
                    len(consul_token) == 0 or
                    consul_token in ["none", "None"]):
                consul_token = None

            try:
                c = consul.Consul(
                    host=consul_host,
                    port=consul_port,
                    scheme=consul_scheme,
                    token=consul_token,
                    verify=consul_verify_ssl
                )
                c.kv.put(consul_key, str(uuid.uuid4()))
            except Exception as e:
                logger.critical(e)
