from vegadns.api import endpoint, app
from vegadns.api.endpoints import domain, domains, record, records, export
from vegadns.api.endpoints import apikeys, apikey
from vegadns.api.endpoints import token


if __name__ == '__main__':
    app.run(debug=True)
