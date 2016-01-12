from email.mime.text import MIMEText
from subprocess import Popen, PIPE

from vegadns.api.config import config
from vegadns.api.email.common import Common


class Sendmail(Common):
    def send(self, to, subject, body, extra_headers):
        # FIXME extra_headers
        msg = MIMEText(body)
        msg["From"] = self.get_support_email()
        msg["To"] = to
        msg["Subject"] = subject

        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(msg.as_string())
