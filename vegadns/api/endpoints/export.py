import hashlib

from flask import Flask, abort, redirect, url_for, make_response
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.audit_log import AuditLog as ModelAuditLog
from vegadns.api.models.recordtypes import RecordType
from vegadns.api.export.tinydns import ExportTinydnsData
from vegadns.validate import Validate


@endpoint
class Export(AbstractEndpoint):
    # Future proofing other exports, but tinydns_data only for now
    route = '/export/<format>'

    # allow for ip auth here
    auth_types = ["basic", "oauth", "ip"]

    def get(self, format):
        if format != 'tinydns':
            abort(400, message="invalid format: " + format)

        records = self.get_records()

        domains = {}

        for record in records:
            if record.domain_id.domain not in domains:
                domains[record.domain_id.domain] = []

            domains[record.domain_id.domain].append(record)

        organized = []
        for key, val in sorted(domains.items()):
            organized.append(
                {
                    'domain_name': key,
                    'records': val
                }
            )

        tinydns = ExportTinydnsData()
        datafile = tinydns.export_domains(organized)

        generation_record_host = config.get(
            'monitoring',
            'vegadns_generation_txt_record'
        )
        if generation_record_host \
           and Validate().record_hostname(generation_record_host):

            timestamp = self.get_latest_log_timestamp()
            md5 = hashlib.md5(datafile + "\n").hexdigest()

            model = ModelRecord()
            model.type = RecordType().set('TXT')
            model.host = generation_record_host
            model.val = str(timestamp) + "-" + md5
            model.ttl = 3600

            generation_record_line = tinydns.data_line_from_model(model)

            datafile += "\n\n# VegaDNS Generation TXT Record\n"
            datafile += generation_record_line.rstrip("\n")

        response = make_response(datafile)
        response.headers['content-type'] = 'text/plain'

        return response

    def get_latest_log_timestamp(self):
        result = ModelAuditLog.select(
            ModelAuditLog.time
        ).order_by(
            -ModelAuditLog.time
        ).limit(1)

        if result:
            return result[0].time
        else:
            return 0

    def get_records(self):
        return (
            ModelRecord.select(ModelDomain, ModelRecord)
            .join(
                ModelDomain,
                on=ModelDomain.domain_id == ModelRecord.domain_id
            )
            .where(ModelDomain.status == 'active')
            .order_by(
                ModelDomain.domain.asc(),
                ModelRecord.type.asc(),
                ModelRecord.host.asc(),
                ModelRecord.val.asc()
            )
        )
