from flask.ext.restful import Resource, request

from vegadns.api.common import Auth
from vegadns.api.models.domain import Domain as ModelDomain


class AbstractEndpoint(Resource):
    auth_required = True

    def __init__(self):
        self.auth = Auth(request, self)
        pass

    def get_read_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_read_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(401, message="Not authorized to access this domain")

    def get_write_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_write_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(401, message="Not authorized to edit this domain")

    def get_delete_domain(self, domain_id):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.get(ModelDomain.domain_id == domain_id)

        if self.auth.account.can_delete_domain(domain_id):
            return self.auth.account.domains[domain_id]["domain"]

        abort(401, message="Not authorized to delete this domain")

    def get_account(self, account_id):
        return ModelAccount.get(ModelAccount.account_id == account_id)
