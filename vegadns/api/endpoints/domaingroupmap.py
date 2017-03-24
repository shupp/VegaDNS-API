from flask import Flask, request
from flask.ext.restful import abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.group import Group as ModelGroup
from vegadns.api.models.domain_group_map import DomainGroupMap as ModelMap


@endpoint
class DomainGroupMap(AbstractEndpoint):
    route = '/domaingroupmaps/<int:map_id>'

    def get(self, map_id):
        try:
            map = self.get_map(map_id)
        except peewee.DoesNotExist:
            abort(404, message="domaingroupmap does not exist")

        formatted = map.format_map(map)

        return {'status': 'ok', 'domaingroupmap': formatted}

    def put(self, map_id):
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        try:
            map = self.get_map(map_id)
        except peewee.DoesNotExist:
            abort(404, message="domaingroupmap does not exist")

        can_read = request.form.get('can_read', 1)
        can_write = request.form.get('can_write', 1)
        can_delete = request.form.get('can_delete', 1)

        # Handle params
        if str(can_read) != "1" and str(can_read) != "0":
            abort(400, message="'can_read' must be 1 or 0")
        can_read = int(can_read)
        if str(can_write) != "1" and str(can_write) != "0":
            abort(400, message="'can_write' must be 1 or 0")
        can_write = int(can_write)
        if str(can_delete) != "1" and str(can_delete) != "0":
            abort(400, message="'can_delete' must be 1 or 0")
        can_delete = int(can_delete)

        # make change
        map.set_perm(map.READ_PERM, can_read)
        map.set_perm(map.WRITE_PERM, can_write)
        map.set_perm(map.DELETE_PERM, can_delete)
        map.save()

        # Log it
        perms = []
        if can_read:
            perms.append("read")
        if can_write:
            perms.append("write")
        if can_delete:
            perms.append("delete")

        self.dns_log(
            map.domain_id.domain_id,
            (
                "Set permissions on " + map.domain_id.domain + " for group " +
                map.group_id.name + " to " + ", ".join(perms)
            )
        )

        new = self.get_map(map_id)

        formatted = new.format_map(new)

        return {'status': 'ok', 'domaingroupmap': formatted}

    def delete(self, map_id):
        if self.auth.account.account_type != 'senior_admin':
            abort(403)
        try:
            map = self.get_map(map_id)
        except peewee.DoesNotExist:
            abort(404, message="domaingroupmap does not exist")

        try:
            map.delete_instance()
        except:
            abort(400, message="unable to delete domaingroupmap")

        # Log it
        self.dns_log(
            map.domain_id.domain_id,
            (
                "Removed " + map.domain_id.domain + " from group " +
                map.group_id.name
            )
        )
        return {'status': 'ok'}

    def get_map(self, map_id):
        return ModelMap.select(ModelMap, ModelGroup, ModelDomain).where(
            ModelMap.map_id == map_id
        ).join(
            ModelGroup,
            on=ModelMap.group_id == ModelGroup.group_id
        ).switch(ModelMap).join(
            ModelDomain,
            on=ModelMap.domain_id == ModelDomain.domain_id
        ).get()
