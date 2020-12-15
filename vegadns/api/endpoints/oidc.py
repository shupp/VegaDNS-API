import logging

from flask import make_response, session
from flask_pyoidc.user_session import UserSession

from vegadns.api import endpoint
from vegadns.api.config import config
from vegadns.api.endpoints import AbstractEndpoint


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

@endpoint
class OidcTest(AbstractEndpoint):
    auth_required = True
    route = '/oidc_test'

    def get(self):
        user_session = UserSession(session)
        response = make_response(user_session.userinfo)
        return response
