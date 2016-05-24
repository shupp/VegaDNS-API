import re
import socket


class ValidateIPPrefix(object):

    @staticmethod
    def ipv4(prefix):
        if prefix is None:
            return False
        for part in prefix.split('.'):
            if len(str(part)) == 0:
                return False
            if int(part) < 0 or int(part) > 255:
                return False
        return True

    @staticmethod
    def ipv6(prefix):
        if prefix is None:
            return False
        regex = re.compile('^([0-9a-fA-F]{4}:){0,7}[0-9a-fA-F]{4}$')
        if regex.match(prefix):
            return True
        return False
