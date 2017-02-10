import time
import json

from flask.ext.restful import Resource, request, abort

from vegadns.api.common import Auth
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.audit_log import AuditLog as ModelAuditLog
from vegadns.api.update_notifications import Notifier


class AbstractEndpoint(Resource):
    version = 1.0
    auth_required = True
    auth_types = ["basic", "oauth", "cookie"]

    def __init__(self):
        self.auth = Auth(request, self)

    def get_read_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_read_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(403, message="Not authorized to access this domain")

    def get_write_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_write_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(403, message="Not authorized to edit this domain")

    def get_delete_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_delete_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(403, message="Not authorized to delete this domain")

    def get_account(self, account_id):
        return ModelAccount.get(ModelAccount.account_id == account_id)

    def get_permissions(self, domain_id):
        if self.auth.account.account_type == "senior_admin":
            return {
                "can_read": True,
                "can_write": True,
                "can_delete": True
            }

        return {
            "can_read": bool(self.auth.account.can_read_domain(domain_id)),
            "can_write": bool(self.auth.account.can_write_domain(domain_id)),
            "can_delete": bool(self.auth.account.can_delete_domain(domain_id))
        }

    def dns_log(self, domain_id, entry):
        log = ModelAuditLog()
        log.name = (self.auth.account.first_name +
                    " " +
                    self.auth.account.last_name)
        log.email = self.auth.account.email
        log.domain_id = domain_id
        log.account_id = self.auth.account.account_id
        log.entry = entry
        log.time = int(time.time())

        try:
            log.save()
            return log
        except:
            # FIXME log error
            pass

    def send_update_notification(self):
        Notifier().send()

    def serialize(self, content):
        return json.dumps(content)

    def sort_query(self, query, params):
        if not hasattr(self, 'sort_fields'):
            return query

        sort_fields = self.sort_fields.keys()
        sort = params.get('sort', None)
        if sort is not None and sort in sort_fields:
            sort_field = self.sort_fields[sort]
            # get direction
            order = params.get('order', None)
            if order is not None and str(order).lower() == 'desc':
                # allow for lists of fields
                if type(sort_field) is list:
                    sort_field[0] = sort_field[0].desc()
                else:
                    sort_field = sort_field.desc()

            if type(sort_field) is list:
                return query.order_by(*sort_field)
            else:
                return query.order_by(sort_field)
        else:
            return query

    def paginate_query(self, query, params):
        perpage = params.get('perpage', None)
        if perpage is None:
            return query

        try:
            perpage = abs(int(perpage))
        except:
            abort(400, message="Invalid value for perpage: " + perpage)

        page = params.get('page', None)
        if page is None:
            page = 1
        else:
            try:
                page = abs(int(page))
            except:
                abort(400, message="Invalid value for page: " + page)

        return query.paginate(page, perpage)
