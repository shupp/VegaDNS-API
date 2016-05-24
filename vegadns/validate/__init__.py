from vegadns.validate.ip import ValidateIPAddress
from vegadns.validate.ip_prefix import ValidateIPPrefix
from vegadns.validate.dns import ValidateDNS
from vegadns.validate.string import ValidateString


class Validate(object):

    def ip_prefix(self, prefix, prefix_type):
        if prefix_type == 'ipv4':
            return self.ipv4_prefix(prefix)
        else:
            return self.ipv6_prefix(prefix)

    def ipv4(self, ipv4_address):
        return ValidateIPAddress.ipv4(ipv4_address)

    def ipv6(self, ipv6_address):
        return ValidateIPAddress.ipv6(ipv6_address)

    def ipv4_prefix(self, prefix):
        return ValidateIPPrefix.ipv4(prefix)

    def ipv6_prefix(self, prefix):
        return ValidateIPPrefix.ipv6(prefix)

    def record_hostname(self, name):
        return ValidateDNS.record_hostname(name)

    def sha256(self, string):
        return ValidateString().sha256(string)

    def uuid(self, string):
        return ValidateString().uuid(string)

    def email(self, email):
        return ValidateString().email(email)
