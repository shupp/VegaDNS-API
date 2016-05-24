from flask.ext.restful import request, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints.records_common import RecordsCommon
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.recordtypes import RecordTypeException
from vegadns.api.models.recordtypes import RecordValueException, RecordType
from vegadns.api.models.domain import Domain as ModelDomain


@endpoint
class Records(RecordsCommon):
    route = '/records'
    sort_fields = {
        'name': ModelRecord.host,
        'value': ModelRecord.val,
        'ttl': ModelRecord.ttl,
        'type': ModelRecord.type,
        'distance': ModelRecord.ttl
    }

    def get(self):
        domain_id = request.args.get('domain_id')

        if domain_id is None:
            abort(400, message="domain_id parameter is required")

        domain_id = int(domain_id)

        # check if the domain exists
        try:
            self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain_id does not exist: " + domain_id)

        if domain_id is None:
            abort(400, message="'domain_id' parameter is required")

        # get domain and check authorization
        self.auth.account.load_domains()
        domain = self.get_read_domain(domain_id)

        record_collection = self.paginate_query(
            domain.get_records(),
            request.args
        )
        record_collection = self.sort_query(record_collection, request.args)

        # Optional search of record name, value, or both
        search_name = request.args.get('search_name')
        if search_name is not None:
            search_name = search_name.replace('*', '%')
            record_collection = record_collection.where(
                (ModelRecord.host ** (search_name + '%'))
            )

        search_value = request.args.get('search_value')
        if search_value is not None:
            search_value = search_value.replace('*', '%')
            record_collection = record_collection.where(
                (ModelRecord.val ** (search_value + '%'))
            )

        filter_record_type = request.args.get('filter_record_type')
        if (filter_record_type is not None):
            try:
                query_record_type = RecordType().set(filter_record_type)
                record_collection = record_collection.where(
                    ModelRecord.type == query_record_type
                )
            except RecordTypeException:
                abort(
                    400,
                    message="Invalid filter_record_type: " + filter_record_type
                )

        total_records = domain.count_records(
            filter_record_type,
            search_name,
            search_value
        )

        records = []
        for record in record_collection:
            recordtype = record.to_recordtype()
            records.append(recordtype.to_dict())

        clean_domain = domain.to_clean_dict()
        if request.args.get('include_permissions', None):
            clean_domain["permissions"] = self.get_permissions(
                domain.domain_id
            )
        return {
            'status': 'ok',
            'total_records': total_records,
            'records': records,
            'domain': clean_domain
        }

    def post(self):
        domain_id = request.form.get('domain_id')

        if domain_id is None:
            abort(400, message="domain_id parameter is required")

        domain_id = int(domain_id)

        # check if the domain exists
        try:
            self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain_id does not exist: " + domain_id)

        # get domain and check authorization
        self.auth.account.load_domains()
        domain = self.get_write_domain(domain_id)

        record_type = request.form.get('record_type')
        try:
            readable_type = RecordType().set(record_type)
        except RecordTypeException:
            abort(400, message="Invalid record_type: " + str(record_type))

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
        try:
            model.save()
        except RecordValueException as e:
            abort(400, message=e.message)

        self.dns_log(
            domain.domain_id,
            (
                "added " + record_type +
                " with host " + model.host +
                " and value " + model.val
            )
        )

        return {'status': 'ok', 'record': model.to_recordtype().to_dict()}, 201
