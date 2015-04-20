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
