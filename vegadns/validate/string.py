import re
import uuid


class ValidateString(object):
    def sha256(self, string):
        return len(string) == 64 and self.is_hex(string)

    def is_hex(self, string):
        regex = re.compile('^[0-9a-fA-F]+$')
        if regex.match(string):
            return True
        else:
            return False

    def uuid(self, string=None, version=4):
        try:
            uuid.UUID(str(string), version=version)
            return True
        except ValueError:
            return False
