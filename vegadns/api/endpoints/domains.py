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
from vegadns.api.models.account_group_map import AccountGroupMap
from vegadns.api.models.domain_group_map import DomainGroupMap


@endpoint
class Domains(AbstractEndpoint):
    route = '/domains'
    sort_fields = {
        'name': ModelDomain.domain,
        'status': [ModelDomain.status, ModelDomain.domain]
    }

    def get(self):
        domains = []
        try:
            domain_list = self.get_domain_list()
        except peewee.DoesNotExist:
            domain_list = []

        # load up permissions if needed
        dgmaps = None
        include_permissions = request.args.get('include_permissions', None)
        if include_permissions:
            # domain group maps query
            dgmaps = DomainGroupMap.select().where(
                DomainGroupMap.group_id << self.get_group_maps()
            )

        total_domains = domain_list.count()

        domain_list = self.paginate_query(
            domain_list,
            request.args
        )
        domain_list = self.sort_query(domain_list, request.args)

        for d in domain_list:
            domain = d.to_clean_dict()
            if include_permissions:
                domain["permissions"] = self.get_permissions(d, dgmaps)
            domains.append(domain)

        return {
            'status': 'ok',
            'domains': domains,
            'total_domains': total_domains
        }

    def get_permissions(self, domain, dgmaps):
        allperms = {
            "can_read": True,
            "can_write": True,
            "can_delete": True
        }
        if self.auth.account.account_type == "senior_admin":
            return allperms

        if domain.owner_id == self.auth.account.account_id:
            return allperms

        for map in dgmaps:
            if map.domain_id == domain.domain_id:
                return {
                    "can_read": map.has_perm(DomainGroupMap.READ_PERM),
                    "can_write": map.has_perm(DomainGroupMap.WRITE_PERM),
                    "can_delete": map.has_perm(DomainGroupMap.DELETE_PERM),
                }

        # should not get here
        raise abort(500, message="Unable to determine domain permissions")

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
        skip_soa = bool(request.form.get("skip_soa", 0))
        model.add_default_records(self, skipSoa=skip_soa)
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
                query = query.where(
                    (ModelDomain.domain ** ('%' + search + '%'))
                )
            return query

        # domain group maps query
        dgmq = DomainGroupMap.select(DomainGroupMap.domain_id).where(
            DomainGroupMap.group_id << self.get_group_maps()
        )

        # domains query
        domainQuery = ModelDomain.select().where(
            (
                (ModelDomain.owner_id == self.auth.account.account_id) |
                (ModelDomain.domain_id << dgmq)
            )
        )

        if (search is not None):
            search = search.replace('*', '%')
            domainQuery = domainQuery.where(
                (ModelDomain.domain ** (search + '%'))
            )

        return domainQuery

    def get_group_maps(self):
        return AccountGroupMap.select(AccountGroupMap.group_id).where(
            AccountGroupMap.account_id == self.auth.account.account_id
        )
