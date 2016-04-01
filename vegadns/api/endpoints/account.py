from flask.ext.restful import abort, request
from flask import make_response
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.account import Account as ModelAccount
from vegadns.api.models.domain import Domain as ModelDomain
from vegadns.validate import Validate


@endpoint
class Account(AbstractEndpoint):

    route = '/accounts/<int:account_id>'

    def get(self, account_id):
        try:
            account = ModelAccount.get(ModelAccount.account_id == account_id)
        except peewee.DoesNotExist:
            abort(404, message="account does not exist")
        return {'status': 'ok', 'account': account.to_clean_dict()}

    def delete(self, account_id):
        if self.auth.account.account_type != "senior_admin":
            abort(403, message="Insufficient privileges to delete account")

        if self.auth.account.account_id == account_id:
            abort(400, message="Sorry, you can't delete yourself")

        try:
            account = ModelAccount.get(ModelAccount.account_id == account_id)
        except peewee.DoesNotExist:
            abort(404, message="account does not exist")

        # update existing domains to be owned by account 0
        domains = ModelDomain.select().where(
            ModelDomain.owner_id == account_id
        )
        for domain in domains:
            domain.owner_id == 0
            domain.save()

        account.delete_instance()

        return {'status': 'ok'}

    def put(self, account_id):
        if self.auth.account.account_type != 'senior_admin':
            if self.auth.account.account_id != account_id:
                abort(
                    403,
                    message="Insufficient privileges to edit this account"
                )

        first_name = request.form.get("first_name", None)
        last_name = request.form.get("last_name", None)

        if first_name is None or last_name is None:
            abort(400, message="first_name and last_name are required")

        email = request.form.get("email", None)
        if not Validate().email(email):
            abort(400, message="invalid email")

        try:
            existing_account = ModelAccount.get(
                ModelAccount.email == email,
                ModelAccount.account_id != account_id
            )
            abort(400, message="Email address already in use")
        except peewee.DoesNotExist:
            # Expected
            pass

        account_type = request.form.get("account_type", None)
        if account_type not in ["senior_admin", "user"]:
            abort(
                400,
                message="account_type must be either system_admin or user"
            )

        status = request.form.get("status", None)
        if status not in ["active", "inactive"]:
            abort(400, message="status must be 'active' or 'inactive'")

        phone = request.form.get("phone", None)
        # Configurable password regex?
        password = request.form.get("password", None)

        try:
            account = ModelAccount.get(ModelAccount.account_id == account_id)
        except peewee.DoesNotExist:
            abort(404, message="Account does not exist")

        account.first_name = first_name
        account.last_name = last_name
        account.email = email
        account.account_type = account_type
        account.phone = phone
        account.status = status
        # only set password if it was provided
        if password is not None:
            account.set_password(password)

        account.save()

        data = {
            "status": "ok",
            "account": account.to_clean_dict()
        }
        response = make_response(self.serialize(data))
        response.mimetype = 'application/json'

        if (password is not None and
           account.account_id == self.auth.account.account_id):

            user_agent = request.headers.get('User-Agent')
            generated_cookie = account.generate_cookie_value(
                account,
                user_agent
            )
            response.set_cookie('vegadns', generated_cookie)

        return response
