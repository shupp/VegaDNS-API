from flask import Flask, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.location import Location as ModelLocation
from vegadns.api.models.record import Record as ModelRecord
from vegadns.api.models.location_prefix import LocationPrefix as ModelPrefix


@endpoint
class Location(AbstractEndpoint):
    route = '/locations/<int:location_id>'

    def get(self, location_id):
        try:
            location = ModelLocation.get(
                ModelLocation.location_id == location_id
            )
        except peewee.DoesNotExist:
            abort(404, message="location not found")

        return {'status': 'ok', 'location': location.to_dict()}

    def put(self, location_id):
        if self.auth.account.account_type != "senior_admin":
            abort(403, message="Insufficient privileges to modify a location")

        try:
            locationdb = ModelLocation.get(
                ModelLocation.location_id == location_id
            )
        except peewee.DoesNotExist:
            abort(404, message="location not found")

        location = request.form.get('location', None)
        if location is not None:
            location_len = len(location)
            if (location_len < 1 or location_len > 2):
                abort(
                    400,
                    message="location parameter must be 1 or two characters"
                )

        location_description = request.form.get('location_description', None)

        # gotta supply something
        if location_description is None and location is None:
            abort(
                400,
                message="You must supply location and or location_description"
            )

        if location is not None:
            locationdb.location = location
            # check for existing duplicate
            try:
                existing_location = ModelLocation.get(
                    ModelLocation.location == location,
                    ModelLocation.location_id != locationdb.location_id
                )
                abort(400, message="Location already in use")
            except peewee.DoesNotExist:
                pass

        if location_description is not None:
            locationdb.location_description = location_description

        locationdb.save()

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok', 'location': locationdb.to_dict()}

    def delete(self, location_id):
        if self.auth.account.account_type != "senior_admin":
            abort(403, message="Insufficient privileges to delete a location")

        try:
            locationdb = ModelLocation.get(
                ModelLocation.location_id == location_id
            )
        except peewee.DoesNotExist:
            abort(404, message="location not found")

        locationdb.delete_prefixes()
        # update records that have this id to null (public)
        query = ModelRecord.update(location_id=None).where(
            ModelRecord.location_id == location_id
        )
        query.execute()
        locationdb.delete_instance()

        # notify listeners of dns data change
        self.send_update_notification()

        return {'status': 'ok'}
