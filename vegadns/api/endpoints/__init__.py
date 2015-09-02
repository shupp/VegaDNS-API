import time
import json

from flask.ext.restful import Resource, request, abort

from vegadns.api.common import Auth
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.audit_log import AuditLog as ModelAuditLog


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

    def serialize(self, content):
        return json.dumps(content)

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
