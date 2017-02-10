import re

from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain


@endpoint
class DomainsDefaultSOA(AbstractEndpoint):
    route = '/domains/<int:domain_id>/create_default_soa'

    def post(self, domain_id):
        try:
            self.auth.account.load_domains()
            domain = self.get_write_domain(domain_id)
        except peewee.DoesNotExist:
            abort(404, message="domain does not exist")

        try:
            soa = domain.add_default_soa_record(self)
        except peewee.DoesNotExist:
            abort(400, message="No default soa record to create from")

        if soa is None:
            abort(400, message="An SOA record already exists for this domain")

        # notify listeners of dns data change
        self.send_update_notification()

        return {
            'status': 'ok',
            'domain': domain.to_clean_dict(),
            'record': soa.to_clean_dict()
        }, 201
