import re

from peewee import IntegerField, CharField, PrimaryKeyField

from vegadns.api.models import database, BaseModel, ensure_validation
from vegadns.validate.dns import ValidateDNS
from vegadns.validate.ip import ValidateIPAddress


class Record(BaseModel):
    distance = IntegerField(null=True)
    domain_id = IntegerField(db_column='domain_id')
    host = CharField()
    port = IntegerField(null=True)
    record_id = PrimaryKeyField()
    ttl = IntegerField()
    type = CharField(null=True)
    val = CharField(null=True)
    weight = IntegerField(null=True)

    def to_recordtype(self):
        instance = AbstractRecordType.singleton(self)
        instance.from_model(self)
        return instance

    class Meta:
        db_table = 'records'

    def validate(self):
        recordtype = self.to_recordtype()
        recordtype.validate()

    @staticmethod
    def hostname_in_domain(hostname, domain):
        p = re.compile(".*" + domain + "([.])?$", re.IGNORECASE)
        m = p.match(hostname)
        return bool(m)


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

    def to_model(self):
        model = Record()
        if self.values.get("record_id") is not None:
            model.record_id = self.values["record_id"]
        model.domain_id = self.values["domain_id"]
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
        self.values['domain_id'] = model.domain_id
        self.values['record_type'] = RecordType().get(model.type)
        self.values['name'] = model.host
        self.values['value'] = model.val
        self.values['ttl'] = model.ttl

    def to_model(self):
        model = super(SOARecord, self).to_model()
        model.host = self.values["name"]
        model.val = self.values["value"]
        model.ttl = self.values["ttl"]

        return model

    def validate_record_hostname(self):
        name = str(self.values.get("name"))
        if not ValidateDNS.record_hostname(name):
            raise RecordValueException("Invalide name: " + name)


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

        # add validation here?
        if defaults is not None:
            for key in self.defaults.keys():
                if key in defaults:
                    self.defaults[key] = defaults[key]

    def from_model(self, model):
        if model.type != 'S':
            raise RecordTypeException('Model type is not S')

        host_split = str(model.host).split(":")
        val_split = str(model.val).split(":")

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

    def to_model(self):
        model = super(SOARecord, self).to_model()
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

    def validate(self):
        # Defaults are good here, might want to come up with more
        # validation though
        self.validate_domain_id()


class NSRecord(CommonRecord):
    record_type = 'NS'

    def validate(self):
        self.validate_domain_id()
        self.validate_record_hostname()

        if ValidateIPAddress.ipv4(name):
            raise RecordValueException(
                "NS record names cannot be an IP address"
            )

        value = str(self.values.get("value"))
        if not ValidateDNS.record_hostname(value):
            raise RecordValueException(
                "Invalide value for NS record: " + value
            )


class ARecord(CommonRecord):
    record_type = 'A'

    def validate(self):
        self.validate_domain_id()
        self.validate_record_hostname()

        ip = str(self.values.get("value"))
        if not ValidateIPAddress.ipv4(ip):
            raise RecordValueException(
                "Invalide IP address: " + ip
            )


class MXRecord(CommonRecord):
    record_type = 'MX'

    def from_model(self, model):
        super(MXRecord, self).from_model(model)

        # add additional values
        self.values['distance'] = model.distance


class CNAMERecord(CommonRecord):
    record_type = 'CNAME'

    def validate(self):
        self.validate_domain_id()
        self.validate_record_hostname()

        value = str(self.values.get("value"))
        if ValidateIPAddress.ipv4(value):
            raise RecordValueException(
                "CNAME records cannot point to an IP address"
            )


class TXTRecord(CommonRecord):
    record_type = 'TXT'

    def validate(self):
        self.validate_domain_id()
        self.validate_record_hostname()


class PTRRecord(CommonRecord):
    record_type = 'PTR'

    def validate(self):
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


class AAAAPTRRecord(CommonRecord):
    record_type = 'AAAA+PTR'


class SRVRecord(CommonRecord):
    record_type = 'SRV'

    def from_model(self, model):
        super(SRVRecord, self).from_model(model)

        # add additional values
        self.values['distance'] = model.distance
        self.values['weight'] = model.weight
        self.values['port'] = model.port


class SPFRecord(CommonRecord):
    record_type = 'SPF'


class RecordType(object):
    record_types = {
        'S': {'name': 'SOA', 'record_class': SOARecord},
        'N': {'name': 'NS', 'record_class': NSRecord},
        'A': {'name': 'A', 'record_class': ARecord},
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
