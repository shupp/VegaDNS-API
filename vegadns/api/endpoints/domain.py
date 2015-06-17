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
            domain = self.get_read_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")
        return {'status': 'ok', 'domain': domain.to_clean_dict()}

    def put(self, domain_id):
        try:
            domain = self.get_write_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")

        # get params
        owner_id = request.form.get('owner_id')
        status = request.form.get('status')

        if owner_id is None and status is None:
            abort(400, message="no parameters provided")

        if owner_id is not None:
            if owner_id == 0:
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
                    401,
                    message="Only senior_admins can change status"
                )
            if status != "active" and status != "inactive":
                abort(
                    400,
                    message="status must be either 'active' or 'inactive'"
                )
            domain.status = status

        domain.save()

        return {'status': 'ok', 'domain': domain.to_clean_dict()}

    def delete(self, domain_id):
        try:
            domain = self.get_delete_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")

        # FIXME delete records first
        domain.delete_instance()

        return {'status': 'ok'}
