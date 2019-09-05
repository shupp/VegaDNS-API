from flask import Flask, request
from flask_restful import abort
from peewee import IntegrityError

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.group import Group as ModelGroup
from vegadns.api.models.account_group_map import AccountGroupMap as ModelMap


@endpoint
class Groups(AbstractEndpoint):
    route = '/groups'

    def post(self):
        if self.auth.account.account_type != 'senior_admin':
            abort(403, message="insufficient privileges")
        name = request.form.get("name", None)

        if name is None:
            abort(400, message="missing 'name' parameter")

        try:
            group = self.create_group(name)
        except IntegrityError:
            abort(400, message="name must be unique")

        return {'status': 'ok', 'group': group.to_dict()}, 201

    def get(self):
        try:
            groups = []
            for group in self.get_group_list():
                groups.append(group.to_dict())
        except Exception:
            abort(404, message="no groups found")
        return {'status': 'ok', 'groups': groups}

    def create_group(self, name):
        group = ModelGroup()
        group.name = name
        group.save()

        return group

    def get_group_list(self):
        if self.auth.account.account_type == 'senior_admin':
            return ModelGroup.select()
        else:
            group_maps = ModelMap.select().where(
                ModelMap.account_id == self.auth.account.account_id
            )
            ids = []
            for group_map in group_maps:
                ids.append(group_map.group_id)
            return ModelGroup.select().where(ModelGroup.group_id << ids)
