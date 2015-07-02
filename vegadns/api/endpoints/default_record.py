from flask.ext.restful import request, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints.records_common import RecordsCommon
from vegadns.api.models.default_record import (
    DefaultRecord as ModelDefaultRecord
)


@endpoint
class DefaultRecord(RecordsCommon):
    route = '/default_records/<int:record_id>'

    def get(self, record_id):
        # only open to senior_admin for now
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        try:
            default_record = self.get_default_record(record_id)
        except peewee.DoesNotExist:
            abort(404, message="default record does not exist")

        recordtype = default_record.to_recordtype()
        return {'status': 'ok', 'default_record': recordtype.to_dict()}

    def put(self, record_id):
        # only open to senior_admin for now
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        try:
            default_record = self.get_default_record(record_id)
        except peewee.DoesNotExist:
            abort(404, message="default record does not exist")

        TypeModel = default_record.to_recordtype()

        self.request_form_to_type_model(request.form, TypeModel, None)

        model = TypeModel.to_model(default_record=True)
        model.save()

        return {
            'status': 'ok',
            'default_record': model.to_recordtype().to_dict()
        }

    def delete(self, record_id):
        # only open to senior_admin for now
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        try:
            default_record = self.get_default_record(record_id)
        except:
            abort(404, message="default record does not exist")

        default_record.delete_instance()

        return {'status': 'ok'}

    def get_default_record(self, record_id):
        return ModelDefaultRecord.get(
            ModelDefaultRecord.record_id == record_id
        )
