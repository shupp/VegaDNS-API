from flask.ext.restful import request, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints.records_common import RecordsCommon
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.recordtypes import RecordTypeException, RecordType
from vegadns.api.models.domain import Domain as ModelDomain


@endpoint
class Records(RecordsCommon):
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

        # get pagination
        page = request.args.get('page', None)
        if (page is not None):
            try:
                page = int(page)
            except:
                abort(400, message="Invalid value for page: " + page)

        perpage = request.args.get('perpage', None)
        if (perpage is not None):
            try:
                perpage = int(perpage)
            except:
                abort(400, message="Invalid value for page: " + perpage)

        record_collection = domain.get_records(page, perpage)
        total_records = domain.count_records()

        records = []
        for record in record_collection:
            recordtype = record.to_recordtype()
            records.append(recordtype.to_dict())

        return {
            'status': 'ok',
            'total_records': total_records,
            'records': records,
            'domain': domain.to_clean_dict()
        }

    def post(self):
        domain_id = request.form.get('domain_id')

        if domain_id is None:
            abort(400, message="domain_id parameter is required")

        # check if the domain exists
        try:
            self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain_id does not exist: " + domain_id)

        # get domain and check authorization
        domain = self.get_write_domain(domain_id)

        record_type = request.form.get('record_type')
        try:
            readable_type = RecordType().set(record_type)
        except RecordTypeException:
            abort(400, message="Invalid record_type: " + record_type)

        # If SOA, make sure a record doesn't yet exist
        if record_type == "SOA":
            try:
                ModelRecord.get(
                    ModelRecord.type == RecordType().set(record_type),
                    ModelRecord.domain_id == domain_id
                )
                abort(400, message="SOA record already exists for this domain")
            except peewee.DoesNotExist:
                pass

        TypeModel = RecordType().get_class(RecordType().set(record_type))()

        self.request_form_to_type_model(request.form, TypeModel, domain)

        TypeModel.values["domain_id"] = domain.domain_id
        model = TypeModel.to_model()
        model.save()

        self.dns_log(
            domain.domain_id,
            (
                "added " + record_type +
                " with host " + model.host +
                " and value " + model.val
            )
        )

        return {'status': 'ok', 'record': model.to_recordtype().to_dict()}, 201
