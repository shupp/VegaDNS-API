from flask.ext.restful import request, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints.records_common import RecordsCommon
from vegadns.api.models.default_record import (
    DefaultRecord as ModelDefaultRecord
)
from vegadns.api.models.recordtypes import RecordTypeException, RecordType


@endpoint
class DefaultRecords(RecordsCommon):
    route = '/default_records'

    def get(self):
        # only open to senior_admin for now
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        record_collection = self.get_default_records()

        filter_record_type = request.args.get('filter_record_type')
        if (filter_record_type is not None):
            try:
                query_record_type = RecordType().set(filter_record_type)
                record_collection = record_collection.where(
                    ModelDefaultRecord.type == query_record_type
                )
            except RecordTypeException:
                abort(
                    400,
                    message="Invalid filter_record_type: " + filter_record_type
                )

        records = []
        for record in record_collection:
            recordtype = record.to_recordtype()
            records.append(recordtype.to_dict())

        return {'status': 'ok', 'default_records': records}

    def post(self):
        # only open to senior_admin for now
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        record_type = request.form.get('record_type')
        try:
            record_type_in_db = RecordType().set(record_type)
        except RecordTypeException:
            abort(400, message="Invalid record_type: " + record_type)

        if record_type in ["AAAA+PTR", "PTR"]:
            abort(
                400,
                message="Sorry, record_type " + record_type +
                        " is not supported for default records"
            )

        # If SOA, make sure a record doesn't yet exist
        if record_type == "SOA":
            try:
                ModelDefaultRecord.get(
                    ModelDefaultRecord.type == record_type_in_db
                )
                abort(400, message="A default SOA record already exists")
            except peewee.DoesNotExist:
                pass

        TypeModel = RecordType().get_class(RecordType().set(record_type))()

        self.request_form_to_type_model(request.form, TypeModel, None)

        model = TypeModel.to_model(default_record=True)
        model.default_type = "system"

        model.save()

        return {
            'status': 'ok',
            'default_record': model.to_recordtype().to_dict()
        }, 201

    def get_default_records(self):
        return ModelDefaultRecord.select().where(
            ModelDefaultRecord.default_type == 'system'
        )
