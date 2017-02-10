from flask import Flask, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.location import Location as ModelLocation
from vegadns.api.models.location_prefix import LocationPrefix as ModelPrefix
from vegadns.validate import Validate


@endpoint
class LocationPrefix(AbstractEndpoint):
    route = '/location_prefixes/<int:prefix_id>'

    def get(self, prefix_id):
        try:
            prefixdb = ModelPrefix.get(ModelPrefix.prefix_id == prefix_id)
            location = ModelLocation.get(
                ModelLocation.location_id == prefixdb.location_id
            )
        except peewee.DoesNotExist:
            abort(404, message="prefix not found")

        return {
            'status': 'ok',
            'location_prefix': prefixdb.to_dict(),
            'location': location.to_dict()
        }

    def put(self, prefix_id):
        if self.auth.account.account_type != "senior_admin":
            abort(
                403,
                message="Insufficient privileges to update a location prefix"
            )

        try:
            prefixdb = ModelPrefix.get(ModelPrefix.prefix_id == prefix_id)
        except peewee.DoesNotExist:
            abort(404, message="prefix not found")

        prefix_type = str(request.form.get('prefix_type', 'ipv4')).lower()
        if prefix_type not in ['ipv4', 'ipv6']:
            abort(400, message='prefix_type must be either ipv4 or ipv6')

        prefix = request.form.get('prefix', None)
        valid_prefix = Validate().ip_prefix(prefix, prefix_type)

        if not valid_prefix:
            abort(
                400,
                message='invalid prefix for prefix_type ' + prefix_type
            )

        prefix_description = request.form.get('prefix_description', None)

        prefixdb.prefix = prefix
        prefixdb.prefix_type = prefix_type
        if prefix_description is not None:
            prefixdb.prefix_description = prefix_description
        try:
            prefixdb.save()
        except peewee.IntegrityError as e:
            abort(
                400,
                message=str(e)
            )

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'location_prefix': prefixdb.to_dict()}

    def delete(self, prefix_id):
        if self.auth.account.account_type != "senior_admin":
            abort(
                403,
                message="Insufficient privileges to delete a location prefix"
            )

        try:
            prefixdb = ModelPrefix.get(
                ModelPrefix.prefix_id == prefix_id
            )
        except peewee.DoesNotExist:
            abort(404, message="location prefix not found")

        prefixdb.delete_instance()

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok'}
