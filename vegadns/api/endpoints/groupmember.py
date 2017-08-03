from flask import Flask, request
from flask.ext.restful import abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.account_group_map import AccountGroupMap as ModelMap
from vegadns.api.models.group import Group as ModelGroup


@endpoint
class GroupMember(AbstractEndpoint):
    route = '/groupmembers/<int:member_id>'

    def get(self, member_id):
        try:
            map = self.get_map(member_id)
            account = self.get_account(map.account_id)
        except peewee.DoesNotExist:
            abort(404, message="groupmember does not exist")

        formatted = map.format_member(map, account)

        return {'status': 'ok', 'groupmember': formatted}

    def put(self, member_id):
        try:
            map = self.get_map(member_id)
            account = self.get_account(map.account_id)
        except peewee.DoesNotExist:
            abort(404, message="groupmember does not exist")

        # Handle params
        is_admin = request.form.get('is_admin')
        if is_admin != "0" and is_admin != "1":
            abort(400, message="is_admin must be 1 or 0")

        # make sure logged in user has perms
        if self.auth.account.account_type != 'senior_admin':
            # check they are a member and is_admin is 1
            try:
                mymap = ModelMap.get(
                    ModelMap.group_id == map.group_id,
                    ModelMap.account_id == self.auth.account.account_id
                )
                if mymap.is_admin != 1:
                    abort(403)
            except peewee.DoesNotExist:
                abort(403)

        # make change
        map.is_admin = int(is_admin)
        map.save()

        formatted = map.format_member(map, account)

        return {'status': 'ok', 'groupmember': formatted}

    def delete(self, member_id):
        try:
            map = self.get_map(member_id)
            account = self.get_account(map.account_id)
        except peewee.DoesNotExist:
            abort(404, message="groupmember does not exist")

        # make sure logged in user has perms
        if self.auth.account.account_type != 'senior_admin':
            # check they are a member and is_admin is 1
            try:
                mymap = ModelMap.get(
                    ModelMap.group_id == map.group_id,
                    ModelMap.account_id == self.auth.account.account_id
                )
                if mymap.is_admin != 1:
                    abort(403)
            except peewee.DoesNotExist:
                abort(403)

        try:
            # FIXME need to delete domain maps when in place
            map.delete_instance()

            # Log change
            group = ModelGroup.get(ModelGroup.group_id == map.group_id)
            self.dns_log(
                0,
                (
                    "Removed " + account.first_name + " " + account.last_name +
                    " from group " + group.name
                )
            )
        except:
            abort(400, message="unable to delete groupmember")
        return {'status': 'ok'}

    def get_map(self, member_id):
        return ModelMap.get(ModelMap.map_id == member_id)

    def get_account(self, account_id):
        return ModelAccount.get(
            ModelAccount.account_id == account_id
        )
