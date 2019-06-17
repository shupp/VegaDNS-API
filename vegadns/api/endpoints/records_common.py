from builtins import str
from flask.ext.restful import request, abort

import peewee

from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.location import Location as ModelLocation
from vegadns.api.models.recordtypes import RecordType


class RecordsCommon(AbstractEndpoint):
    def request_form_to_type_model(self, request_form, TypeModel, domain):
        # switch on type for now
        common_types = [
            "A", "A+PTR", "CNAME", "NS",
            "TXT", "PTR", "AAAA", "AAAA+PTR", "SPF"
        ]
        if TypeModel.record_type in common_types:
            if domain is not None:
                self.check_domain_suffix(domain.domain)

            TypeModel.values["name"] = request_form.get("name")
            TypeModel.values["value"] = request_form.get("value")
            TypeModel.values["ttl"] = request_form.get("ttl", 3600)
        elif TypeModel.record_type == "MX":
            if domain is not None:
                self.check_domain_suffix(domain.domain)

            TypeModel.values["name"] = request_form.get("name")
            TypeModel.values["value"] = request_form.get("value")
            TypeModel.values["distance"] = request_form.get("distance", 0)
            TypeModel.values["ttl"] = request_form.get("ttl", 3600)
        elif TypeModel.record_type == "SRV":
            if domain is not None:
                self.check_domain_suffix(domain.domain)

            TypeModel.values["name"] = request_form.get("name")
            TypeModel.values["value"] = request_form.get("value")
            TypeModel.values["distance"] = request_form.get("distance", 0)
            TypeModel.values["weight"] = request_form.get("weight")
            TypeModel.values["port"] = request_form.get("port")
            TypeModel.values["ttl"] = request_form.get("ttl", 3600)
        elif TypeModel.record_type == "SOA":
            TypeModel.values["email"] = request_form.get("email")
            TypeModel.values["nameserver"] = request_form.get("nameserver")
            TypeModel.values["ttl"] = request_form.get("ttl", 86400)
            TypeModel.values["refresh"] = request_form.get("refresh", 16374)
            TypeModel.values["retry"] = request_form.get("retry", 2048)
            TypeModel.values["expire"] = request_form.get("expire", 1048576)
            TypeModel.values["minimum"] = request_form.get("minimum", 2560)
            TypeModel.values["serial"] = request_form.get("serial", "")
        elif TypeModel.record_type == "CAA":
            TypeModel.values["name"] = request_form.get("name")
            TypeModel.values["ttl"] = request_form.get("ttl", 3600)
            TypeModel.values["flag"] = request_form.get("flag", 0)
            TypeModel.values["tag"] = request_form.get("tag")
            TypeModel.values["tagval"] = request_form.get("tagval")
        else:
            raise Exception("Unsupported record type")

        if TypeModel.record_type != "SOA":
            # Add location_id for non SOA records

            location_id = request_form.get("location_id", None)
            if location_id is not None and str(location_id).isdigit():
                try:
                    locationdb = ModelLocation.get(
                        ModelLocation.location_id == location_id
                    )
                except peewee.DoesNotExist:
                    abort(
                        400,
                        message="location_id does not exist"
                    )

            # Map null/none to None type
            if str(location_id).lower() in ["null", "none", ""]:
                location_id = None
            TypeModel.values["location_id"] = location_id

    def check_domain_suffix(self, domain):
        # make sure hostname ends in domain name
        name = request.form.get("name")
        if not name or not ModelRecord.hostname_in_domain(name, domain):
            abort(
                400,
                message="Name does not end in domain name: " + str(name)
            )

    def get_domain(self, domain_id):
        return ModelDomain.get(ModelDomain.domain_id == domain_id)
