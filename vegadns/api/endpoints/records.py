from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.models.record import Record as ModelRecord


@endpoint
class Records(Resource):
    route = '/records'

    def get(self):
        domain_id = request.args.get('domain_id')
        if domain_id is None:
            abort(400, message="'domain_id' parameter is required")

        try:
            records = []
            for record in self.get_record_list(domain_id):
                records.append(record.to_dict())
        except:
            abort(404, message="no records found")
        return {'status': 'ok', 'records': records}

    def get_record_list(self, domain_id):
        # FIXME need authorization
        return ModelRecord.select().where(ModelRecord.domain_id == domain_id)
