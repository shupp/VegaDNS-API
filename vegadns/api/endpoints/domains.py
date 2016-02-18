import re

from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort

import peewee

import vegadns.api.email
import vegadns.api.email.common
from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.group import Group as ModelGroup


@endpoint
class Domains(AbstractEndpoint):
    route = '/domains'

    def get(self):
        domains = []
        try:
            domain_list = self.get_domain_list()
        except peewee.DoesNotExist:
            domain_list = []

        for d in domain_list:
            domain = d.to_clean_dict()
            if request.args.get('include_permissions', None):
                domain["permissions"] = self.get_permissions(d.domain_id)
            domains.append(domain)

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

            self.dns_log(
                model.domain_id,
                "Added domain " + model.domain + " with status " + model.status
            )
        except ValueError:
            abort(400, message="Invalid parameters")
        except peewee.IntegrityError:
            # race condition, unique constraint will catch it
            abort(400, message="Domain already exists")

        # add default records
        model.add_default_records(self)
        default_records = model.get_records()
        records = []
        for record in default_records:
            records.append(record.to_clean_dict())

        if self.auth.account.account_type != 'senior_admin':
            common = vegadns.api.email.common.Common()
            to = common.get_support_email()
            subject = "New Inactive Domain Created"
            msg_body = "Inactive domain \"" + model.domain + \
                "\" added by " + self.auth.account.email + ".\n\n" + \
                "Thanks,\n\nVegaDNS"

            vegadns.api.email.send(to, subject, msg_body)

        return {
            'status': 'ok',
            'domain': model.to_clean_dict(),
            'records': records
        }, 201

    def get_domain_list(self):
        search = request.args.get('search', None)

        if self.auth.account.account_type == 'senior_admin':
            query = ModelDomain.select()
            if (search is not None):
                search = search.replace('*', '%')
                query = query.where((ModelDomain.domain ** (search + '%')))
            return query

        # FIXME - more complex query needed to support search and
        # load_domains/permission needs rather than post filter

        domains = []
        self.auth.account.load_domains()
        for domain_id in self.auth.account.domains:
            if self.auth.account.can_read_domain(domain_id):
                if search is not None:
                    search = search.replace('*', '.*')
                    p = re.compile("^" + search + ".*$", re.IGNORECASE)
                    if p.match(
                        self.auth.account.domains[domain_id]["domain"].domain
                    ):
                        domains.append(
                            self.auth.account.domains[domain_id]["domain"]
                        )
                else:
                    domains.append(
                        self.auth.account.domains[domain_id]["domain"]
                    )

        return domains
