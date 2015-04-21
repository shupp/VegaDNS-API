import re
import socket


class Validate(object):

    @staticmethod
    def ipv4(ipv4_address):
        try:
            socket.inet_aton(ipv4_address)
        except socket.error:
            return False
        return ipv4_address.count('.') == 3

    @staticmethod
    def ipv6(ipv6_address):
        try:
            socket.inet_pton(socket.AF_INET6, ipv6_address)
        except socket.error:
            return False
        return True

    @staticmethod
    def record_hostname(hostname):
        # All record hostnames must be at least a third level
        if hostname.count('.') <= 1:
            return False

        # Currently only allowing a-z,0-9,- etc per old app
        # May want to revisit this for non-alphanumeric support
        p = re.compile(
            '^([\*a-z0-9-\/]+[\.])+[a-z0-9-]+[\.]{0,1}$',
            re.IGNORECASE
        )

        print p.match(hostname)
        if p.match(hostname):
            return True
        return False
