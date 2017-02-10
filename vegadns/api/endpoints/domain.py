from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.account import Account as ModelAccount


@endpoint
class Domain(AbstractEndpoint):
    route = '/domains/<int:domain_id>'

    def get(self, domain_id):
        try:
            self.auth.account.load_domains()
            domain = self.get_read_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")
        domain = domain.to_clean_dict()
        if request.args.get('include_permissions', None):
            domain["permissions"] = self.get_permissions(domain["domain_id"])
        return {'status': 'ok', 'domain': domain}

    def put(self, domain_id):
        try:
            self.auth.account.load_domains()
            domain = self.get_write_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")

        # get params
        owner_id = request.form.get('owner_id')
        status = request.form.get('status')

        if owner_id is None and status is None:
            abort(400, message="no parameters provided")

        if owner_id is not None:
            if int(owner_id) == 0:
                domain.owner_id = 0
            else:
                try:
                    new_owner = self.get_account(owner_id)
                    domain.owner_id = owner_id
                except peewee.DoesNotExist:
                    abort(400, message="owner_id does not exist")

        if status is not None:
            if self.auth.account.account_type != 'senior_admin':
                abort(
                    403,
                    message="Only senior_admins can change status"
                )
            if status != "active" and status != "inactive":
                abort(
                    400,
                    message="status must be either 'active' or 'inactive'"
                )
            domain.status = status

        domain.save()

        # logging
        log_msgs = []
        if owner_id is not None:
            log_msgs.append("owner id set to " + owner_id)
        if status is not None:
            log_msgs.append("status set to " + status)
        self.dns_log(domain.domain_id, ", ".join(log_msgs))

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'domain': domain.to_clean_dict()}

    def delete(self, domain_id):
        try:
            self.auth.account.load_domains()
            domain = self.get_delete_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")

        log_domain_id = domain.domain_id
        log_msg = "deleted domain " + domain.domain

        domain.delete_domain_group_maps()
        domain.delete_records()
        domain.delete_instance()

        self.dns_log(log_domain_id, log_msg)

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok'}
