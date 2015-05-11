import re


class ValidateString(object):
    def sha256(self, string):
        return len(string) == 64 and self.is_hex(string)

    def is_hex(self, string):
        regex = re.compile('^[0-9a-fA-F]+$')
        if regex.match(string):
            return True
        else:
            return False
