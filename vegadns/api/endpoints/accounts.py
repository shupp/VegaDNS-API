from flask import Flask
from flask_restful import abort, request
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.validate import Validate


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

    def post(self):
        if self.auth.account.account_type != 'senior_admin':
            abort(403, message="Insufficient privileges to create accounts")
        first_name = request.form.get("first_name", None)
        last_name = request.form.get("last_name", None)

        if first_name is None or last_name is None:
            abort(400, message="first_name and last_name are required")

        email = request.form.get("email", None)
        if not Validate().email(email):
            abort(400, message="invalid email")

        try:
            existing_account = ModelAccount.get(ModelAccount.email == email)
            abort(400, message="Email address already in use")
        except peewee.DoesNotExist:
            # Expected
            pass

        account_type = request.form.get("account_type", None)
        if account_type not in ["senior_admin", "user"]:
            abort(
                400,
                message="account_type must be either senior_admin or user"
            )

        phone = request.form.get("phone", "")
        # Configurable password regex?
        password = request.form.get("password", None)

        account = ModelAccount()
        account.first_name = first_name
        account.last_name = last_name
        account.email = email
        account.account_type = account_type
        account.phone = phone
        account.status = 'active'
        account.set_password(password)

        account.save()

        return {'status': 'ok', 'account': account.to_clean_dict()}, 201

    def get_account_list(self):
        query = ModelAccount.select()
        search = request.args.get('search', None)
        if (search is not None):
            query = query.where(
                (ModelAccount.first_name ** (search + '%')) |
                (ModelAccount.last_name ** (search + '%')) |
                (ModelAccount.email ** ('%' + search + '%'))
            )

        return query
