from flask import Flask, abort, redirect, url_for
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount


@endpoint
class Accounts(AbstractEndpoint):
    route = '/accounts'

    def get(self):
        try:
            accounts = []
            for account in self.get_account_list():
                accounts.append(account.to_clean_dict())
        except:
            abort(404, message="no accounts found")
        return {'status': 'ok', 'accounts': accounts}

    def get_account_list(self):
        return ModelAccount.select()  # FIXME need authorization
