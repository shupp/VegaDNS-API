import subprocess
import logging

from flask import Flask, abort, make_response
from flask.ext.restful import Resource, Api, abort

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


@endpoint
class UpdateData(AbstractEndpoint):
    route = '/update-local-tinydns-data'

    def get(self):
        if self.auth.account.account_type != 'senior_admin':
            abort(403, message="insufficient privileges")

        try:
            output = subprocess.check_output(
                ["sudo", "/var/www/vegadns2/bin/update-data.sh"],
                stderr=subprocess.STDOUT
            )
        except Exception as e:
            logger.exception(e)

        response = make_response(output)
        response.headers['content-type'] = 'text/plain'

        return response
