import re

from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort, reqparse

import peewee

import vegadns.api.email
import vegadns.api.email.common
from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.domain import Record as ModelRecord
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
        in_global_acl = self.auth.account.in_global_acl_emails(
            self.auth.account.email
        )
        try:
            domain_list = self.get_domain_list(in_global_acl)
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
                domain["permissions"] = self.get_permissions(
                    d, dgmaps, in_global_acl
                )
            domains.append(domain)

        return {
            'status': 'ok',
            'domains': domains,
            'total_domains': total_domains
        }

    def get_permissions(self, domain, dgmaps, in_global_acl=False):
        allperms = {
            "can_read": True,
            "can_write": True,
            "can_delete": True
        }
        if self.auth.account.account_type == "senior_admin" or in_global_acl:
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
        parser = reqparse.RequestParser()
        parser.add_argument(
            'domain',
            required=True,
            location=['form', 'json'],
            help='domain parameter is required'
        )
        parser.add_argument(
            'move_colliding_records',
            type=bool,
            location=['form', 'json'],
            default=False
        )
        parser.add_argument(
            'skip_soa',
            type=bool,
            location=['form', 'json'],
            default=False
        )
        parser.add_argument(
            'skip_default_records',
            type=bool,
            location=['form', 'json'],
            default=False
        )
        args = parser.parse_args()

        # Lower case the domain
        domain = args['domain'].lower()

        # check for duplicate first
        try:
            ModelDomain.get(ModelDomain.domain == domain)
            abort(400, message="Domain already exists")
        except peewee.DoesNotExist:
            pass

        # check for duplicate records
        duplicate_records = ModelRecord().select().where(
            (ModelRecord.host ** ('%.' + domain)) |
            (ModelRecord.host == domain)
        )

        move_colliding_records = False
        if duplicate_records.count() > 0:
            move_colliding_records = args['move_colliding_records']
            if (move_colliding_records is True and
                    self.auth.account.account_type != 'senior_admin'):

                m = "You must be a senior_admin to move colliding records"
                abort(403, message=m)
            if move_colliding_records is False:
                m = "Unable to create domain, there are colliding records"
                abort(409, message=m)

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
        records = []
        if args['skip_default_records'] is False:
            model.add_default_records(self, skipSoa=args['skip_soa'])
            default_records = model.get_records()
            for record in default_records:
                records.append(record.to_clean_dict())

        # move colliding records
        if move_colliding_records is True:
            for dr in duplicate_records:
                dr.domain_id = model.domain_id
                dr.save()
                records.append(dr.to_clean_dict())

        if self.auth.account.account_type != 'senior_admin':
            common = vegadns.api.email.common.Common()
            to = common.get_support_email()
            subject = "New Inactive Domain Created"
            msg_body = "Inactive domain \"" + model.domain + \
                "\" added by " + self.auth.account.email + ".\n\n" + \
                "Thanks,\n\nVegaDNS"

            vegadns.api.email.send(to, subject, msg_body)

        # notify listeners of dns data change
        self.send_update_notification()

        return {
            'status': 'ok',
            'domain': model.to_clean_dict(),
            'records': records
        }, 201

    def get_domain_list(self, in_global_acl=False):
        search = request.args.get('search', None)

        if self.auth.account.account_type == 'senior_admin' or in_global_acl:
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
