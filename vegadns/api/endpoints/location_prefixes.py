from flask import Flask, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.location import Location
from vegadns.api.models.location_prefix import LocationPrefix
from vegadns.validate import Validate


@endpoint
class LocationPrefixes(AbstractEndpoint):
    route = '/location_prefixes'

    def get(self):
        location_id = self.get_location_id()

        # make sure location exists
        try:
            location = Location.get(Location.location_id == location_id)
        except peewee.DoesNotExist:
            abort(404, message="location_id does not exist")

        query = LocationPrefix.select().where(
            LocationPrefix.location_id == location_id
        )
        prefixes = []
        for prefix in query:
            prefixes.append(prefix.to_dict())

        return {
            'status': 'ok',
            'location_prefixes': prefixes,
            'location': location.to_dict()
        }

    def post(self):
        if self.auth.account.account_type != "senior_admin":
            abort(
                403,
                message="Insufficient privileges to create a location prefix"
            )

        location_id = self.get_location_id()

        # make sure the location exists
        try:
            locationdb = Location.get(Location.location_id == location_id)
        except peewee.DoesNotExist:
            abort(400, message="location_id does not exist")

        prefix_type = str(request.form.get('prefix_type', 'ipv4')).lower()
        if prefix_type not in ['ipv4', 'ipv6']:
            abort(400, message='prefix_type must be either ipv4 or ipv6')

        prefix = request.form.get('prefix', None)

        if prefix is None or not Validate().ip_prefix(prefix, prefix_type):
            abort(
                400,
                message='invalid prefix for prefix_type ' + prefix_type
            )

        prefix_description = request.form.get('prefix_description', None)
        new_prefix = LocationPrefix()
        new_prefix.location_id = location_id
        new_prefix.prefix = prefix
        new_prefix.prefix_type = prefix_type
        if prefix_description is not None:
            new_prefix.prefix_description = prefix_description

        try:
            new_prefix.save()
        except peewee.IntegrityError as e:
            abort(
                400,
                message=str(e)
            )

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'location_prefix': new_prefix.to_dict()}

    def get_location_id(self):
        if request.method == 'GET':
            location_id = request.args.get("location_id", None)
        else:
            location_id = request.form.get("location_id", None)

        if (location_id is None) or not (str(location_id).isdigit()):
            abort(400, message="location_id parameter is required")

        return location_id
