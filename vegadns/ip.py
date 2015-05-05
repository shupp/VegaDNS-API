import netaddr


class IPv6(object):
    def uncompress(self, ip):
        try:
            ip = netaddr.IPAddress(ip)
            return ip.format(netaddr.ipv6_verbose)
        except netaddr.core.AddrFormatError:
            raise IPException('Invalid IPv6 address: ' + ip)


class IPException(Exception):
    pass
