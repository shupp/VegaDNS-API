from flask import Flask, request
from flask.ext.restful import abort
from peewee import IntegrityError

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.group import Group as ModelGroup
from vegadns.api.models.account_group_map import AccountGroupMap as ModelMap


@endpoint
class Group(AbstractEndpoint):
    route = '/groups/<int:group_id>'

    def get(self, group_id):
        try:
            group = self.get_group(group_id)
        except:
            abort(404, message="group not found")
        return {'status': 'ok', 'group': group.to_dict()}

    def put(self, group_id):
        # only senior_admin can modify the group name
        if self.auth.account.account_type != 'senior_admin':
            abort(403, message="insufficient privileges")

        name = request.form.get("name", None)
        if not name:
            abort(400, message="missing or empty 'name' parameter")

        try:
            group = self.get_group(group_id)
        except:
            abort(404, message="group not found")

        try:
            group.name = name
            group.save()
        except IntegrityError:
            abort(400, message="name must be unique")

        return {'status': 'ok', 'group': group.to_dict()}

    def get_group(self, group_id):
        if self.auth.account.account_type != 'senior_admin':
            # DoesNotExist will be raised if map doesn't exist
            group_map = ModelMap.get(
                ModelMap.account_id == self.auth.account.account_id,
                ModelMap.group_id == group_id
            )

        return ModelGroup.get(ModelGroup.group_id == group_id)
