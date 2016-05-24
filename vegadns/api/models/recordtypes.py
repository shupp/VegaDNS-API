import re

from vegadns.api.models import ensure_validation
import vegadns.api.models.record
import vegadns.api.models.default_record
from vegadns.validate.dns import ValidateDNS
from vegadns.validate.ip import ValidateIPAddress
from vegadns.validate import Validate


class RecordException(Exception):
    pass


class RecordTypeException(Exception):
    pass


class RecordValueException(ValueError):
    pass


class AbstractRecordType(object):
    def __init__(self, defaults=None):
        self.defaults = {}
        self.values = {}

        self.set_defaults(defaults)

    def set_defaults(self, defaults):
        if defaults is not None:
            for key in self.defaults.keys():
                if key in defaults:
                    self.defaults[key] = defaults[key]

    @ensure_validation
    def save():
        raise RecordException('Method not defined')

    @ensure_validation
    def update():
        raise RecordException('Method not defined')

    def delete():
        raise RecordException(
            'Do not use delete here, use it at the model level'
        )

    def validate():
        raise RecordException(
            'Validation not implemented'
        )

    def from_model(self, model):
        raise RecordException(
            'Method not defined'
        )

    def to_model(self, default_record=False):
        if default_record:
            model = vegadns.api.models.default_record.DefaultRecord()
        else:
            model = vegadns.api.models.record.Record()
            model.domain_id = self.values["domain_id"]
        if self.values.get("record_id") is not None:
            model.record_id = self.values["record_id"]
        model.type = RecordType().set(self.record_type)

        return model

    def from_form_data(self, form):
        raise RecordException(
            'Method not defined'
        )

    def to_dict(self):
        return self.values

    def validate_domain_id(self):
        domain_id = self.values.get("domain_id")
        if not domain_id:
            raise RecordValueException("domain_id is not set")

    @staticmethod
    def singleton(model):
        cls_name = RecordType().get_class(model.type)
        instance = cls_name()
        return instance


class CommonRecord(AbstractRecordType):
    # Will result in RecordTypeException if not set in subclass
    record_type = None

    def from_model(self, model):
        if self.record_type != RecordType().get(model.type):
            raise RecordTypeException('Model type is not ' + self.record_type)

        self.values['record_id'] = model.record_id
        if type(model) is vegadns.api.models.record.Record:
            self.values['domain_id'] = model.domain_id
        self.values['record_type'] = RecordType().get(model.type)
        self.values['name'] = model.host
        self.values['value'] = model.val
        self.values['ttl'] = model.ttl
        if hasattr(model, 'location_id'):
            self.values['location_id'] = model.location_id

    def to_model(self, default_record=False):
        model = super(CommonRecord, self).to_model(default_record)
        model.host = self.values["name"]
        model.val = self.values["value"]
        model.ttl = self.values["ttl"]
        if "location_id" in self.values:
            model.location_id = self.values["location_id"]

        return model

    def validate_record_hostname(self, default_record=False):
        name = str(self.values.get("name"))
        if default_record:
            test_name = name.replace("DOMAIN", "example.com")
        else:
            test_name = name

        if not ValidateDNS.record_hostname(test_name):
            raise RecordValueException("Invalid name: " + name)


class SOARecord(AbstractRecordType):
    record_type = "SOA"

    def __init__(self, defaults=None):
        self.values = {}
        self.defaults = {
            "ttl": "86400",
            "refresh": "16384",
            "retry": "2048",
            "expire": "1048576",
            "minimum": "2560",
            "serial": ""
        }

        self.set_defaults(defaults)

    def from_model(self, model):
        if model.type != 'S':
            raise RecordTypeException('Model type is not S')

        host_split = str(model.host).split(":")
        val_split = str(model.val).split(":")

        if type(model) is vegadns.api.models.record.Record:
            self.values['domain_id'] = model.domain_id
        self.values['record_id'] = model.record_id
        self.values['record_type'] = 'SOA'

        self.values['email'] = host_split[0]
        self.values['nameserver'] = host_split[1]

        if model.ttl:
            self.values['ttl'] = model.ttl
        else:
            self.values['ttl'] = self.defaults['ttl']

        if val_split[0]:
            self.values['refresh'] = val_split[0]
        else:
            self.values['refresh'] = self.defaults['refresh']

        if len(val_split) >= 2 and val_split[1]:
            self.values['retry'] = val_split[1]
        else:
            self.values['retry'] = self.defaults['retry']

        if len(val_split) >= 3 and val_split[2]:
            self.values['expire'] = val_split[2]
        else:
            self.values['expire'] = self.defaults['expire']

        if len(val_split) >= 4 and val_split[3]:
            self.values['minimum'] = val_split[3]
        else:
            self.values['minimum'] = self.defaults['minimum']

        if len(val_split) >= 5 and val_split[4]:
            self.values['serial'] = val_split[4]
        else:
            self.values['serial'] = self.defaults['serial']

    def to_model(self, default_record=False):
        model = super(SOARecord, self).to_model(default_record)
        model.host = ":".join(str(i) for i in [
            self.values["email"],
            self.values["nameserver"]
        ])
        model.val = ":".join(str(i) for i in [
            self.values["refresh"],
            self.values["retry"],
            self.values["expire"],
            self.values["minimum"],
            self.values["serial"]
        ])

        return model

    def validate(self, default_record=False):
        # Defaults are good here, might want to come up with more
        # validation though
        if not default_record:
            self.validate_domain_id()


class NSRecord(CommonRecord):
    record_type = 'NS'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        value = str(self.values.get("value"))
        if ValidateIPAddress.ipv4(value):
            raise RecordValueException(
                "NS record names cannot be an IP address"
            )

        if not ValidateDNS.record_hostname(value):
            raise RecordValueException(
                "Invalid value for NS record: " + value
            )


class ARecord(CommonRecord):
    record_type = 'A'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        ip = str(self.values.get("value"))
        if not ValidateIPAddress.ipv4(ip):
            raise RecordValueException(
                "Invalid IP address: " + ip
            )


class APTRRecord(ARecord):
    record_type = 'A+PTR'


class MXRecord(CommonRecord):
    record_type = 'MX'

    def __init__(self, defaults=None):
        if defaults is None:
            defaults = {"distance": 0}

        super(MXRecord, self).__init__(defaults)

    def from_model(self, model):
        super(MXRecord, self).from_model(model)

        # add additional values
        self.values['distance'] = model.distance

    def to_model(self, default_record=False):
        model = super(MXRecord, self).to_model(default_record)
        model.distance = self.values.get("distance", 0)

        return model

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        ip = str(self.values.get("value"))
        if ValidateIPAddress.ipv4(ip):
            raise RecordValueException("MX records cannot be an IP address")

        distance = str(self.values.get("distance"))
        if not distance.isdigit():
            raise RecordValueException("Invalid MX distance: " + distance)


class CNAMERecord(CommonRecord):
    record_type = 'CNAME'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        value = str(self.values.get("value"))
        if ValidateIPAddress.ipv4(value):
            raise RecordValueException(
                "CNAME records cannot point to an IP address"
            )


class TXTRecord(CommonRecord):
    record_type = 'TXT'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)


class PTRRecord(CommonRecord):
    record_type = 'PTR'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()

        p = re.compile('^.*\.in-addr.arpa[.]?$', re.IGNORECASE)
        name = str(self.values.get("name"))
        m = p.match(name)
        if not m:
            raise RecordValueException(
                "PTR records must end in in-addr.arpa: " + name
            )


class AAAARecord(CommonRecord):
    record_type = 'AAAA'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        ip = str(self.values.get("value"))
        if not Validate().ipv6(ip):
            raise RecordValueException(
                "Invalid IPv6 address: " + ip
            )


class AAAAPTRRecord(AAAARecord):
    record_type = 'AAAA+PTR'


class SRVRecord(CommonRecord):
    record_type = 'SRV'

    def from_model(self, model):
        super(SRVRecord, self).from_model(model)

        # add additional values
        self.values['distance'] = model.distance
        self.values['weight'] = model.weight
        self.values['port'] = model.port

    def to_model(self, default_record=False):
        model = super(SRVRecord, self).to_model(default_record)
        model.distance = self.values.get("distance", 0)
        model.weight = self.values.get("weight")
        model.port = self.values.get("port")

        return model

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)

        # check _service._protocol format
        name = str(self.values.get("name"))
        p = re.compile('^_.*\._.*$', re.IGNORECASE)
        if not p.match(name):
            raise RecordValueException(
                "SRV record be in the format _service._protocol: " + name
            )

        # check range for distance/weight/port
        mydict = {
            "distance": self.values.get("distance"),
            "weight": self.values.get("weight"),
            "port": self.values.get("port")
        }

        for k, v in mydict.items():
            if not self.check_number_range(v):
                raise RecordValueException(
                    "SRV " + k + " must be a numeric value between 0 and 65535"
                )

    def check_number_range(self, number):
        return (str(number).isdigit() and 0 <= int(number) <= 65535)


class SPFRecord(CommonRecord):
    record_type = 'SPF'

    def validate(self, default_record=False):
        if not default_record:
            self.validate_domain_id()
        self.validate_record_hostname(default_record)


class RecordType(object):
    record_types = {
        'S': {'name': 'SOA', 'record_class': SOARecord},
        'N': {'name': 'NS', 'record_class': NSRecord},
        'A': {'name': 'A', 'record_class': ARecord},
        '=': {'name': 'A+PTR', 'record_class': APTRRecord},
        '3': {'name': 'AAAA', 'record_class': AAAARecord},
        '6': {'name': 'AAAA+PTR', 'record_class': AAAAPTRRecord},
        'M': {'name': 'MX', 'record_class': MXRecord},
        'P': {'name': 'PTR', 'record_class': PTRRecord},
        'T': {'name': 'TXT', 'record_class': TXTRecord},
        'C': {'name': 'CNAME', 'record_class': CNAMERecord},
        'V': {'name': 'SRV', 'record_class': SRVRecord},
        'F': {'name': 'SPF', 'record_class': SPFRecord}
    }

    def get(self, type):
        if type in self.record_types.keys():
            return self.record_types[type]['name']
        else:
            raise RecordTypeException('Invalid record type')

    def set(self, type):
        if not type:
            raise RecordTypeException('Invalid record type')

        for k, v in self.record_types.items():
            if v['name'] == type.upper():
                return k

        raise RecordTypeException('Invalid record type')

    def get_class(self, type):
        upper = type.upper()
        if upper not in self.record_types.keys():
            raise RecordTypeException('Invalid record type')

        return self.record_types[upper]['record_class']

    def to_record_model(self):
        pass
