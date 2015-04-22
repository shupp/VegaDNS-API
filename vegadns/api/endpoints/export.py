from flask import Flask, abort, redirect, url_for, make_response
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.export.tinydns import ExportTinydnsData


@endpoint
class Export(Resource):
    # Future proofing other exports, but tinydns_data only for now
    route = '/export/<format>'

    def get(self, format):
        if format != 'tinydns':
            abort(400, message="invalid format: " + format)

        domains = []
        domain_list = self.get_domain_list()
        for domain in domain_list:
            # may want to batch here rather than get serially
            records = self.get_record_list(domain.domain_id)
            domains.append(
                {
                    'domain_name': domain.domain,
                    'records': records
                }
            )

        tinydns = ExportTinydnsData()
        datafile = tinydns.export_domains(domains)
        response = make_response(datafile)
        response.headers['content-type'] = 'text/plain'

        return response

    def get_domain_list(self):
        # FIXME need IP authorization
        return ModelDomain.select().where(ModelDomain.status == 'active')

    def get_record_list(self, domain_id):
        return ModelRecord.select().where(ModelRecord.domain_id == domain_id)
