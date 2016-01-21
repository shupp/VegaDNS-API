import smtplib

from vegadns.api.config import config
from vegadns.api.email.common import Common


class SMTP(Common):
    def send(self, to, subject, body, extra_headers):
        # FIXME extra_headers
        smtp_host = config.get("email", "smtp_host")
        smtp_port = config.get("email", "smtp_port")

        smtp_keyfile = None
        if len(config.get("email", "smtp_keyfile")):
            smtp_keyfile = config.get("email", "smtp_keyfile")

        smtp_certfile = None
        if len(config.get("email", "smtp_certfile")):
            smtp_certfile = config.get("email", "smtp_certfile")

        if config.get('email', 'smtp_ssl') in ["True", "true"]:
            server = smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                None,
                smtp_keyfile,
                smtp_certfile
            )
        else:
            server = smtplib.SMTP(
                smtp_host,
                smtp_port
            )

            if config.get("email", "smtp_tls") in ["True", "true"]:
                server.starttls(smtp_keyfile, smtp_certfile)

        if config.get("email", "smtp_auth") in ["True", "true"]:
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
