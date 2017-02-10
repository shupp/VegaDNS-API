from flask.ext.restful import request, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints.records_common import RecordsCommon
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.recordtypes import RecordType, RecordValueException


@endpoint
class Record(RecordsCommon):
    route = '/records/<int:record_id>'

    def get(self, record_id):
        try:
            record = self.get_record(record_id)
        except peewee.DoesNotExist:
            abort(404, message="record does not exist")

        # check authorization
        if not self.auth.account.in_global_acl_emails(self.auth.account.email):
            self.auth.account.load_domains()
            domain = self.get_read_domain(record.domain_id)

        recordtype = record.to_recordtype()
        return {'status': 'ok', 'record': recordtype.to_dict()}

    def put(self, record_id):
        try:
            record = self.get_record(record_id)
        except peewee.DoesNotExist:
            abort(404, message="record does not exist")

        TypeModel = record.to_recordtype()

        # get domain and check authorization
        domain = self.auth.account.get_domain_by_record_acl(
            record.domain_id,
            record.host,
            TypeModel.record_type
        )
        if domain is False:
            self.auth.account.load_domains()
            domain = self.get_write_domain(record.domain_id)

        self.request_form_to_type_model(request.form, TypeModel, domain)

        try:
            model = TypeModel.to_model()
            # recheck auth in case host changed
            if record.host != model.host:
                domain = self.auth.account.get_domain_by_record_acl(
                    record.domain_id,
                    model.host,
                    TypeModel.record_type
                )
                if domain is False:
                    self.auth.account.load_domains()
                    domain = self.get_read_domain(record.domain_id)

            model.save()
        except RecordValueException as e:
            abort(400, message=str(e))

        self.dns_log(
            domain.domain_id,
            (
                "updated record " + str(model.record_id) +
                " of type " + RecordType().get(model.type) +
                " with host " + model.host +
                " and value " + model.val
            )
        )

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'record': model.to_recordtype().to_dict()}

    def delete(self, record_id):
        try:
            record = self.get_record(record_id)
        except:
            abort(404, message="record does not exist")

        TypeModel = record.to_recordtype()

        # load domain and check authorization
        domain = self.auth.account.get_domain_by_record_acl(
            record.domain_id,
            record.host,
            TypeModel.record_type
        )
        if domain is False:
            self.auth.account.load_domains()
            domain = self.get_delete_domain(record.domain_id)

        record.delete_instance()

        self.dns_log(
            domain.domain_id,
            (
                "deleted " + RecordType().get(record.type) +
                " with host " + record.host +
                " and value " + record.val
            )
        )

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok'}

    def get_record(self, record_id):
        return ModelRecord.get(ModelRecord.record_id == record_id)

    def check_domain_suffix(self, domain):
        # make sure hostname ends in domain name
        name = request.form.get("name")
        if not name or not ModelRecord.hostname_in_domain(name, domain):
            abort(
                400,
                message="Name does not end in domain name: " + str(name)
            )
