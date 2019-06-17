from builtins import oct
from builtins import str
from builtins import range
from builtins import object
import struct

from vegadns.ip import IPv6
from vegadns.validate.ip import ValidateIPAddress
from vegadns.api.export import ExportException


class ExportTinydnsData(object):
    locations = None

    def data_line_from_model(self, model):
        locstring = ""
        if self.locations is not None and model.location_id is not None:
            for loc in self.locations:
                if loc.location_id == model.location_id:
                    locstring = "::" + loc.location
                    break

        # A record
        if model.type == "A":
            return "+" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + locstring + "\n"
        # A+PTR record
        if model.type == "=":
            return "=" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + locstring + "\n"
        # MX record
        elif model.type == "M":
            return "@" + model.host + "::" + model.val + ":" + \
                   str(model.distance) + ":" + str(model.ttl) + \
                   locstring + "\n"
        # PTR record
        elif model.type == "P":
            return "^" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + locstring + "\n"
        # TXT record
        elif model.type == "T":
            return "'" + model.host + ":" + model.val.replace(":", r"\072") + \
                   ":" + str(model.ttl) + locstring + "\n"
        # SPF record (rfc 4408, deprecated)
        elif model.type == "F":
            rdata_len = self.dec_to_oct_tinydns(len(model.val))
            return ":" + model.host + ":99:" + rdata_len + \
                   model.val.replace(":", r"\072") + ":" + \
                   str(model.ttl) + locstring + "\n"
        # CNAME record
        elif model.type == "C":
            return "C" + model.host + ":" + model.val + \
                ":" + str(model.ttl) + locstring + "\n"
        # SOA record
        elif model.type == "S":
            soa = model.to_recordtype().to_dict()

            return "Z" + model.domain_id.domain + \
                ":" + soa['nameserver'] + \
                ":" + soa['email'] + \
                ":" + soa['serial'] + \
                ":" + soa['refresh'] + \
                ":" + soa['retry'] + \
                ":" + soa['expire'] + \
                ":" + soa['minimum'] + \
                ":" + str(soa['ttl']) + \
                "\n"
        # NS record
        elif model.type == "N":
            return "&" + model.host + \
                "::" + model.val + \
                ":" + str(model.ttl) + locstring + \
                "\n"

        # SRV record
        elif model.type == "V":
            encoded = self.encode_rdata(
                'cccq',
                [
                    model.distance,
                    model.weight,
                    model.port,
                    model.val.rstrip('.')
                ]
            )
            return ":" + model.host + \
                ":33:" + \
                encoded + \
                ":" + str(model.ttl) + locstring + \
                "\n"

        elif model.type == "3" or model.type == "6":
            # AAAA Record
            # FIXME - exception handling
            out = ""
            uncompressed = IPv6().uncompress(model.val)
            formatted_octal = self.ipv6_to_tinydns(uncompressed)

            out += ":" + model.host + ":28:" + formatted_octal + \
                ":" + str(model.ttl) + locstring + "\n"

            # if 6, then build corresponding PTR
            if model.type == "6":
                ptr = self.ipv6_to_ptr(uncompressed)
                out += "^" + ptr + ":" + model.host + ":" + str(model.ttl) + \
                    "\n"

            return out

        # CAA record
        elif model.type == "E":
            caa_split = model.val.split(":", 2)
            return ":" + model.host + \
                ":257:" + "\%03o" % int(caa_split[0]) + \
                "\%03o" % len(caa_split[1]) + \
                "".join("\%03o" % ord(c) for c in caa_split[1]) + \
                "".join("\%03o" % ord(c) for c in caa_split[2]) + \
                ":" + str(model.ttl) + \
                "\n"

    def export_domain(self, domain_name, records):
        output = "#" + domain_name + "\n"
        formatted_records = ""
        for record in records:
            formatted_record = self.data_line_from_model(record)
            if formatted_record is None:
                # fixme, need to finish record support
                pass
            else:
                formatted_records = formatted_records + formatted_record

        return output + formatted_records

    def export_domains(self, domains, locations=None):
        self.locations = locations

        output = ""
        for domain in domains:
            output += "\n"
            formatted = self.export_domain(
                domain['domain_name'],
                domain['records']
            )
            output = output + formatted

        return output.rstrip("\n")

    def dec_to_oct_tinydns(self, decimal):
        padded_octal = oct(int(decimal)).lstrip('0').zfill(3)
        return '\\' + padded_octal

    def ipv6_to_tinydns(self, uncompressed):
        out = ""
        for part in uncompressed.split(':'):
            # Check IPv4 dotted decimal usage
            if ValidateIPAddress.ipv4(part):
                for ipv4 in part.split('.'):
                    out += dec_to_oct_tinydns(ipv4)
            else:
                # characters 1 and 2
                out += "\\" + self.base_convert(
                    part[0] + part[1], 16, 8
                ).lstrip('0').zfill(3)

                # characters 3 and 4
                out += "\\" + self.base_convert(
                    part[2] + part[3], 16, 8
                ).lstrip('0').zfill(3)

        return out

    # http://www.php2python.com/wiki/function.base-convert/
    def base_convert(self, number, fromBase, toBase):
        try:
            # Convert number to base 10
            base10 = int(number, fromBase)
        except ValueError:
            raise

        if toBase < 2 or toBase > 36:
            raise NotImplementedError

        output_value = ''
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        sign = ''

        if base10 == 0:
            return '0'
        elif base10 < 0:
            sign = '-'
            base10 = -base10

        # Convert to base toBase
        s = ''
        while base10 != 0:
            r = base10 % toBase
            r = int(r)
            s = digits[r] + s
            base10 //= toBase

        output_value = sign + s
        return output_value

    def ipv6_to_ptr(self, ipv6):
        uncompressed = IPv6().uncompress(ipv6)
        parts = reversed(uncompressed.split(':'))
        characters = []
        for part in parts:
            characters += reversed(part)

        return ".".join(characters) + ".ip6.arpa"

    def encode_rdata(self, format, values):
        rdata = ""
        if len(format) != len(values):
            raise Exception("rdata value count mismatch in format")

        for i in range(len(format)):
            if format[i] == "c":
                rdata += self.encode_rdata_octets(values[i])
            elif format[i] == "q":
                rdata += self.encode_rdata_qname(values[i])
            else:
                raise ExportException("Invalid rdata format: " + format[i])

        return rdata

    def encode_rdata_octets(self, value):
        # Big Endian 16 bit MSB LSB encoding for decimal values to rdata octets
        packed = struct.pack(">H", value)
        unpacked = struct.unpack(">BB", packed)
        return "\\" + oct(int(unpacked[0])).lstrip("0").zfill(3) + \
            "\\" + oct(int(unpacked[1])).lstrip("0").zfill(3)

    def encode_rdata_qname(self, hostname):
        # QNAME(RFC 1035 section 4.1.2) encoding for url to octets
        qnameparts = hostname.split(".")
        qname = ""
        for part in qnameparts:
            qname += "\\" + oct(len(part)).lstrip("0").zfill(3) + part

        # add term octect for QNAME
        qname += "\\000"

        return qname
