from vegadns.api.config import config


class Common(object):
    def get_support_email(self):
        support_name = config.get('email', 'support_name')
        support_email = config.get('email', 'support_email')

        return support_name + " <" + support_email + ">"
