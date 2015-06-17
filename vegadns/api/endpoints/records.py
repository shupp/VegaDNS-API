from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.domain import Domain as ModelDomain


@endpoint
class Records(AbstractEndpoint):
    route = '/records'

    def get(self):
        domain_id = request.args.get('domain_id')

        if domain_id is None:
            abort(400, message="domain_id parameter is required")

        # check if the domain exists
        try:
            self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, "domain_id does not exist: " + domain_id)

        if domain_id is None:
            abort(400, message="'domain_id' parameter is required")

        # get domain and check authorization
        domain = self.get_read_domain(domain_id)
        record_collection = domain.get_records()

        records = []
        for record in record_collection:
            recordtype = record.to_recordtype()
            records.append(recordtype.to_dict())

        return {'status': 'ok', 'records': records}

    def get_domain(self, domain_id):
        return ModelDomain.get(ModelDomain.domain_id == domain_id)
