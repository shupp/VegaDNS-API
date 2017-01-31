from flask import Flask, request
from flask.ext.restful import abort
import peewee
from peewee import IntegrityError

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.group import Group as ModelGroup
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.api.models.domain_group_map import DomainGroupMap as ModelMap


@endpoint
class DomainGroupMaps(AbstractEndpoint):
    route = '/domaingroupmaps'

    def get(self):
        domain_id = request.args.get('domain_id')
        group_id = request.args.get('group_id')
        if domain_id is None and group_id is None:
            abort(
                400,
                message="'domain_id' or 'group_id' parameter is required"
            )

        collection = self.get_domain_group_maps(domain_id, group_id)
        maps = []
        for m in collection:
            formatted = m.format_map(m)
            maps.append(formatted)

        return {'status': 'ok', 'domaingroupmaps': maps}

    def post(self):
        if self.auth.account.account_type != 'senior_admin':
            abort(403)

        group_id = request.form.get('group_id')
        domain_id = request.form.get('domain_id')
        can_read = request.form.get('can_read', 1)
        can_write = request.form.get('can_write', 1)
        can_delete = request.form.get('can_delete', 1)

        # Handle params
        if group_id is None:
            abort(400, message="'group_id' parameter is required")
        if domain_id is None:
            abort(400, message="'domain_id' parameter is required")
        if str(can_read) != "1" and str(can_read) != "0":
            abort(400, message="'can_read' must be 1 or 0")
        can_read = int(can_read)
        if str(can_write) != "1" and str(can_write) != "0":
            abort(400, message="'can_write' must be 1 or 0")
        can_write = int(can_write)
        if str(can_delete) != "1" and str(can_delete) != "0":
            abort(400, message="'can_delete' must be 1 or 0")
        can_delete = int(can_delete)

        # Verify group
        try:
            group = self.get_group(group_id)
        except peewee.DoesNotExist:
            abort(400, message="Group does not exist")

        # Verify domain
        try:
            domain = self.get_domain(domain_id)
        except peewee.DoesNotExist:
            abort(400, message="Domain does not exist")

        # Make sure map doesn't exist
        try:
            map = self.get_map(domain_id, group_id)
            abort(400, message="Group is already mapped to domain")
        except peewee.DoesNotExist:
            pass

        # Add map
        newmap = self.create_map(
            domain_id,
            group_id,
            can_read,
            can_write,
            can_delete
        )

        # Log it
        perms = []
        if can_read:
            perms.append("read")
        if can_write:
            perms.append("write")
        if can_delete:
            perms.append("delete")

        self.dns_log(
            domain_id,
            (
                "Added domain " + domain.domain + " to group " +
                group.name + " with perms " + ", ".join(perms)
            )
        )

        # Do new lookup with joined tables for formatting
        map = self.get_map(domain_id, group_id)
        formatted = map.format_map(map)

        return {'status': 'ok', 'domaingroupmap': formatted}, 201

    def get_domain_group_maps(self, domain_id, group_id):
        if domain_id is not None and group_id is not None:
            return ModelMap.select(ModelMap, ModelGroup, ModelDomain).where(
                ModelMap.domain_id == domain_id,
                ModelMap.group_id == group_id
            ).join(
                ModelGroup,
                on=ModelMap.group_id == ModelGroup.group_id
            ).switch(ModelMap).join(
                ModelDomain,
                on=ModelMap.domain_id == ModelDomain.domain_id
            )
        if domain_id is not None:
            return ModelMap.select(ModelMap, ModelGroup, ModelDomain).where(
                ModelMap.domain_id == domain_id
            ).join(
                ModelGroup,
                on=ModelMap.group_id == ModelGroup.group_id
            ).switch(ModelMap).join(
                ModelDomain,
                on=ModelMap.domain_id == ModelDomain.domain_id
            )
        elif group_id is not None:
            return ModelMap.select(ModelMap, ModelGroup, ModelDomain).where(
                ModelMap.group_id == group_id
            ).join(
                ModelGroup,
                on=ModelMap.group_id == ModelGroup.group_id
            ).switch(ModelMap).join(
                ModelDomain,
                on=ModelMap.domain_id == ModelDomain.domain_id
            )

    def get_domain(self, domain_id):
        return ModelDomain.get(
            ModelDomain.domain_id == domain_id
        )

    def get_group(self, group_id):
        return ModelGroup.get(
            ModelGroup.group_id == group_id
        )

    def get_map(self, domain_id, group_id):
        return ModelMap.select(ModelMap, ModelGroup, ModelDomain).where(
            ModelMap.domain_id == domain_id,
            ModelMap.group_id == group_id
        ).join(
            ModelGroup,
            on=ModelMap.group_id == ModelGroup.group_id
        ).switch(ModelMap).join(
            ModelDomain,
            on=ModelMap.domain_id == ModelDomain.domain_id
        ).get()

    def create_map(self, domain_id, group_id, can_read, can_write, can_delete):
        map = ModelMap()
        map.domain_id = domain_id
        map.group_id = group_id
        map.set_perm(map.READ_PERM, can_read)
        map.set_perm(map.WRITE_PERM, can_write)
        map.set_perm(map.DELETE_PERM, can_delete)
        map.save()

        return map
