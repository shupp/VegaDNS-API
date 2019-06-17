from builtins import str
from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.apikey import ApiKey as ModelApiKey
from vegadns.api.models.account import Account as ModelAccount


@endpoint
class ApiKeys(AbstractEndpoint):
    route = '/apikeys'

    def get(self):
        if self.auth.account.account_type == "senior_admin":
            account_ids = request.args.get(
                "account_ids",
                str(self.auth.account.account_id)
            ).replace(" ", "").split(",")
        else:
            account_ids = [self.auth.account.account_id]

        keys = []
        for key in self.get_apikey_list(account_ids):
            keys.append(key.to_dict())
        return {'status': 'ok', 'apikeys': keys}

    def post(self):
        description = request.form.get("description", "")
        account_id = request.form.get("account_id", None)

        if account_id is not None:
            if account_id != self.auth.account.account_id:
                if self.auth.account.account_type != "senior_admin":
                    message = ("Insufficient privileges to create an api key "
                               "for another user")
                    abort(403, message=message)

            try:
                account = ModelAccount.get(
                    ModelAccount.account_id == account_id
                )
                account_id = account.account_id
            except peewee.DoesNotExist:
                abort(400, message="account_id does not exist")
        else:
            account_id = self.auth.account.account_id

        apikey = self.create_api_key(description, account_id)

        return {'status': 'ok', 'apikey': apikey.to_dict()}, 201

    def get_apikey_list(self, account_ids):
        return ModelApiKey.select().where(
            ModelApiKey.account_id << account_ids
        ).where(ModelApiKey.deleted != 1)

    def create_api_key(self, description, account_id):
        apikey = ModelApiKey()
        apikey.account_id = account_id
        apikey.description = description
        apikey.generate()
        apikey.save()

        return apikey
