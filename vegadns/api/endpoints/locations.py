from flask import Flask, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.location import Location
from vegadns.api.models.location_prefix import LocationPrefix


@endpoint
class Locations(AbstractEndpoint):
    route = '/locations'

    def get(self):
        query = Location.select()
        locations = []
        for location in query:
            locations.append(location.to_dict())

        return {'status': 'ok', 'locations': locations}

    def post(self):
        if self.auth.account.account_type != "senior_admin":
            abort(403, message="Insufficient privileges to create a location")

        location = request.form.get('location', None)
        location_len = len(location)
        if location_len < 1 or location_len > 2:
            abort(
                400,
                message="location parameter must be 1 or two characters"
            )

        try:
            existing_location = Location.get(
                Location.location == location
            )
            abort(400, message="Location already in use")
        except peewee.DoesNotExist:
            pass

        location_description = request.form.get('location_description', None)
        new_location = Location()
        new_location.location = location
        new_location.location_description = location_description
        new_location.save()

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'location': new_location.to_dict()}, 201
