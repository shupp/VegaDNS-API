import smtplib

from vegadns.api.config import config
from vegadns.api.email.common import Common


class SMTP(Common):
    def send(self, to, subject, body, extra_headers):
        # FIXME extra_headers
        server = smtplib.SMTP('localhost')
        if smtp_auth in ["True", "true"]:
            server.login(
                config.get('email', 'smtp_user'),
                config.get('email', 'smtp_password')
            )

        message = 'Subject: %s\n\n%s' % (subject, body)
        server.sendmail(
            self.get_support_email(),
            to,
            message
        )
        server.quit()
