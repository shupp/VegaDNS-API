from builtins import str
from flask import Flask, request
from flask_restful import abort
import peewee
from peewee import IntegrityError

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.group import Group as ModelGroup
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.account_group_map import AccountGroupMap as ModelMap


@endpoint
class GroupMembers(AbstractEndpoint):
    route = '/groupmembers'

    def get(self):
        group_id = request.args.get('group_id')
        if group_id is None:
            abort(400, message="'group_id' parameter is required")

        maps = self.get_group_members(group_id)
        groupmembers = []
        for m in maps:
            formatted = m.format_member(m, m.account_id)
            groupmembers.append(formatted)

        return {'status': 'ok', 'groupmembers': groupmembers}

    def post(self):
        group_id = request.form.get('group_id')
        account_id = request.form.get('account_id')
        is_admin = request.form.get('is_admin', 0)

        # Handle params
        if group_id is None:
            abort(400, message="'group_id' parameter is required")
        if account_id is None:
            abort(400, message="'account_id' parameter is required")
        if str(is_admin) != "1" and str(is_admin) != "0":
            abort(400, message="'is_admin' must be 1 or 0")
        is_admin = int(is_admin)

        # Verify user
        try:
            account = self.get_account(account_id)
        except peewee.DoesNotExist:
            abort(400, message="Account does not exist")

        if account.status != "active":
            abort(400, message="Account is not active")

        # Make sure map doesn't exist
        try:
            map = self.get_map(account_id, group_id)
            abort(400, message="Account is already a group member")
        except peewee.DoesNotExist:
            pass

        # make sure logged in user has perms
        if self.auth.account.account_type != 'senior_admin':
            # check they are a member and is_admin is 1
            try:
                mymap = self.get_map(
                    self.auth.account.account_id,
                    group_id
                )
                if mymap.is_admin != 1:
                    abort(403)
            except peewee.DoesNotExist:
                abort(403)

        # Add map
        newmap = self.create_map(account_id, group_id, is_admin)
        formatted = newmap.format_member(newmap, account)

        # Log change
        group = ModelGroup.get(ModelGroup.group_id == group_id)
        self.dns_log(
            0,
            (
                "Added " + account.first_name + " " + account.last_name +
                " to group " + group.name
            )
        )

        return {'status': 'ok', 'groupmember': formatted}, 201

    def get_group_members(self, group_id):
        return ModelMap.select(ModelMap, ModelAccount).where(
            ModelMap.group_id == group_id
        ).join(
            ModelAccount,
            on=ModelMap.account_id == ModelAccount.account_id
        )

    def get_account(self, account_id):
        return ModelAccount.get(
            ModelAccount.account_id == account_id
        )

    def get_map(self, account_id, group_id):
        return ModelMap.get(
            ModelMap.account_id == account_id,
            ModelMap.group_id == group_id
        )

    def create_map(self, account_id, group_id, is_admin):
        map = ModelMap()
        map.account_id = account_id
        map.group_id = group_id
        map.is_admin = is_admin
        map.save()

        return map
