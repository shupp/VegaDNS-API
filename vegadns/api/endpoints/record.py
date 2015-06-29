from flask.ext.restful import abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.record import Record as ModelRecord


@endpoint
class Record(AbstractEndpoint):
    route = '/records/<int:record_id>'

    def get(self, record_id):
        try:
            record = self.get_record(record_id)
        except peewee.DoesNotExist:
            abort(404, message="record does not exist")

        # check authorization
        domain = self.get_read_domain(record.domain_id)

        recordtype = record.to_recordtype()
        return {'status': 'ok', 'record': recordtype.to_dict()}

    def delete(self, record_id):
        try:
            record = self.get_record(record_id)
        except:
            abort(404, message="record does not exist")

        # check authorization
        domain = self.get_delete_domain(record.domain_id)
        record.delete_instance()

        return {'status': 'ok'}

    def get_record(self, record_id):
        return ModelRecord.get(ModelRecord.record_id == record_id)
