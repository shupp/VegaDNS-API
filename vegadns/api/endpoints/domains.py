from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort

import peewee

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

    def post(self):
        domain = request.form.get("domain")
        if domain is None:
            abort(400, message="domain parameter is required")

        # check for duplicate first
        try:
            ModelDomain.get(ModelDomain.domain == domain)
            abort(400, message="Domain already exists")
        except peewee.DoesNotExist:
            pass

        model = ModelDomain()
        model.domain = domain
        if self.auth.account.account_type != 'senior_admin':
            model.status = 'inactive'
            model.owner_id = self.auth.account.account_id

        try:
            model.save()
        except ValueError:
            abort(400, message="Invalid parameters")
        except peewee.IntegrityError:
            # race condition, unique constraint will catch it
            abort(400, message="Domain already exists")

        # add default records
        model.add_default_records()
        default_records = model.get_records()
        records = []
        for record in default_records:
            records.append(record.to_dict())

        if self.auth.account.account_type != 'senior_admin':
            # FIXME send email to admins
            pass

        return {
            'status': 'ok',
            'domain': model.to_clean_dict(),
            'records': records
        }, 201

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
