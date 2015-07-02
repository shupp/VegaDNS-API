import os

from vegadns.api import endpoint, app
from vegadns.api.endpoints import domain, domains, record, records, export
from vegadns.api.endpoints import apikeys, apikey, groups, group
from vegadns.api.endpoints import token, groupmember, groupmembers, accounts
from vegadns.api.endpoints import domaingroupmap, domaingroupmaps
from vegadns.api.endpoints import default_record, default_records
from vegadns.api.endpoints import updatedata

profile = os.environ.get('PROFILE', None)
debug = bool(os.environ.get('DEBUG', None))

if profile:
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0')
