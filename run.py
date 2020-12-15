import os

from vegadns.api import endpoint, app
from vegadns.api.endpoints import domain, domains, record, records, export
from vegadns.api.endpoints import domains_default_soa
from vegadns.api.endpoints import apikeys, apikey, groups, group
from vegadns.api.endpoints import token, groupmember, groupmembers, accounts
from vegadns.api.endpoints import domaingroupmap, domaingroupmaps
from vegadns.api.endpoints import default_record, default_records
from vegadns.api.endpoints import updatedata, account, login, logout
from vegadns.api.endpoints import healthcheck, audit_logs
from vegadns.api.endpoints import password_reset_token, password_reset_tokens
from vegadns.api.endpoints import locations, location
from vegadns.api.endpoints import location_prefixes, location_prefix
from vegadns.api.endpoints import swagger
from vegadns.api.endpoints import release_version
from vegadns.api.endpoints import oidc

from vegadns.api.config import config

from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

profile = os.environ.get('PROFILE', None)
debug = True
if str(os.environ.get('DEBUG', True)).lower() not in ['true', '1']:
    debug = False

app.DEBUG = debug

if profile:
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


if config.getboolean('oidc', 'enabled'):
    SSO = 'SSO'
    app.config['OIDC_REDIRECT_URI'] = config.get('oidc', 'redirect_uri')

    SSO_CONFIG = ProviderConfiguration(
        issuer= config.get('oidc', 'issuer'),
        client_metadata=ClientMetadata(
            config.get('oidc', 'client'), config.get('oidc', 'secret')
            ),
        auth_request_params={
            'scope':
            [item.strip() for item in config.get('oidc', 'scope').split(',')]
        }
    )

    app.config['SECRET_KEY'] = config.get('auth', 'cookie_secret')
    app.config['OIDC_AUTH'] = OIDCAuthentication({SSO: SSO_CONFIG}, app)
    app.config['OIDC_DECORATOR'] = app.config['OIDC_AUTH'].oidc_auth(SSO)

if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0')
