import logging

from vegadns.api.config import config
from vegadns.api.email import sendmail, smtp


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def send(to, subject, body, extra_headers=False):
    if config.get('email', 'email_method') == "sendmail":
        transport = sendmail.Sendmail()
    else:
        transport = smtp.SMTP()

    try:
        transport.send(to, subject, body, extra_headers)
    except Exception, e:
        # don't block on email issues
        logger.exception(e)
