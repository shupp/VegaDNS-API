from flask import Flask, abort, redirect, url_for, make_response
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.export.tinydns import ExportTinydnsData


@endpoint
class Export(AbstractEndpoint):
    # Future proofing other exports, but tinydns_data only for now
    route = '/export/<format>'

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
        response = make_response(datafile)
        response.headers['content-type'] = 'text/plain'

        return response

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
