from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.record import Record as ModelRecord, RecordType
from vegadns.api.models.record import RecordTypeException
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
            abort(404, message="domain_id does not exist: " + domain_id)

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

    def post(self):
        domain_id = request.form.get('domain_id')

        if domain_id is None:
            abort(400, message="domain_id parameter is required")

        # check if the domain exists
        try:
            self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain_id does not exist: " + domain_id)

        if domain_id is None:
            abort(400, message="'domain_id' parameter is required")

        # get domain and check authorization
        domain = self.get_write_domain(domain_id)

        record_type = request.form.get('record_type')
        try:
            RecordType().set(record_type)
        except RecordTypeException:
            abort(400, message="Invalid record_type: " + record_type)

        # make sure hostname ends in domain name
        name = request.form.get("name")
        if not name or not ModelRecord.hostname_in_domain(name, domain.domain):
            abort(400, message="Name does not end in domain name: " + name)

        TypeModel = RecordType().get_class(record_type)()

        # switch on type for now
        if TypeModel.record_type == "A":
            TypeModel.values["name"] = request.form.get("name")
            TypeModel.values["value"] = request.form.get("value")
            TypeModel.values["ttl"] = request.form.get("ttl", 3600)
            TypeModel.values["domain_id"] = domain.domain_id
            model = TypeModel.to_model()
        else:
            raise Exception("Unsupported record type")

        model.save()

        return {'status': 'ok', 'record': model.to_recordtype().to_dict()}, 201

    def get_domain(self, domain_id):
        return ModelDomain.get(ModelDomain.domain_id == domain_id)
