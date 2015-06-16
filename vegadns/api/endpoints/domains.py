from flask import Flask, abort, redirect, url_for
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.group import Group as ModelGroup


@endpoint
class Domains(AbstractEndpoint):
    route = '/domains'

    def get(self):
        try:
            domains = []
            for domain in self.get_domain_list():
                domains.append(domain.to_dict())
        except:
            abort(404, message="no domains found")
        return {'status': 'ok', 'domains': domains}

    def get_domain_list(self):
        if self.auth.account.account_type == 'senior_admin':
            return ModelDomain.select()

        domains = []
        self.auth.account.load_domains()
        for domain_id in self.auth.account.domains:
            if self.auth.account.can_read_domain(domain_id):
                domains.append(
                    self.auth.account.domains[domain_id]["domain"]
                )

        return domains
