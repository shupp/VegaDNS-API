from flask import Flask, abort, redirect, url_for, request
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.apikey import ApiKey as ModelApiKey


@endpoint
class ApiKeys(AbstractEndpoint):
    route = '/apikeys'

    def get(self):
        keys = []
        for key in self.get_apikey_list():
            keys.append(key.to_dict())
        return {'status': 'ok', 'apikeys': keys}

    def post(self):
        description = request.form.get("description", "")

        apikey = self.create_api_key(description, self.auth.account.account_id)

        return {'status': 'ok', 'apikey': apikey.to_dict()}, 201

    def get_apikey_list(self):
        return ModelApiKey.select().where(
            ModelApiKey.account_id == self.auth.account.account_id
        )

    def create_api_key(self, description, account_id):
        apikey = ModelApiKey()
        apikey.account_id = account_id
        apikey.description = description
        apikey.generate()
        apikey.save()

        return apikey
