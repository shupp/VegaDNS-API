from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort

import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.apikey import ApiKey as ModelApiKey


@endpoint
class ApiKey(AbstractEndpoint):
    route = '/apikeys/<int:apikey_id>'

    def get(self, apikey_id):
        try:
            apikey = self.get_apikey(apikey_id)
        except peewee.DoesNotExist:
            abort(404, message="api key not found")
        return {'status': 'ok', 'apikey': apikey.to_dict()}

    def put(self, apikey_id):
        try:
            apikey = self.get_apikey(apikey_id)
        except peewee.DoesNotExist:
            abort(404, message="api key not found")

        data = request.form

        if 'description' in list(data.keys()):
            apikey.description = data['description']
        if 'deleted' in list(data.keys()):
            apikey.deleted = int(data['deleted'])

        apikey.save()

        return {'status': 'ok', 'apikey': apikey.to_dict()}

    def delete(self, apikey_id):
        try:
            apikey = self.get_apikey(apikey_id)
        except peewee.DoesNotExist:
            abort(404, message="api key not found")

        apikey.deleted = 1
        apikey.save()

        return {'status': 'ok'}

    def get_apikey(self, apikey_id):
        if self.auth.account.account_type == "senior_admin":
            return ModelApiKey.get(
                ModelApiKey.apikey_id == apikey_id,
                ModelApiKey.deleted == 0
            )
        else:
            return ModelApiKey.get(
                ModelApiKey.apikey_id == apikey_id,
                ModelApiKey.account_id == self.auth.account.account_id,
                ModelApiKey.deleted == 0
            )
