from flask import Flask, abort, request
from flask.ext.restful import Resource, Api, abort
import peewee

from vegadns.api import endpoint
from vegadns.api.endpoints import AbstractEndpoint
from vegadns.api.models.audit_log import AuditLog as ModelAuditLog


@endpoint
class AuditLogs(AbstractEndpoint):
    route = '/audit_logs'
    sort_fields = {
        'time': ModelAuditLog.time,
        'log_id': ModelAuditLog.log_id,
        'domain_id': ModelAuditLog.domain_id
    }

    def get(self):
        self.auth.account.load_domains()

        domain_id_list = []
        requested_domain_ids = []
        domain_ids = request.args.get(
            "domain_ids",
            None
        )
        search = request.args.get("search", "")

        # check for provided list of domain ids
        if domain_ids is not None:
            requested_domain_ids = domain_ids.replace(" ", "").split(",")

            if self.auth.account.account_type != "senior_admin":
                # check read permissions
                for d in requested_domain_ids:
                    if not str.isdigit(str(d)):
                        abort(400, message="invalid domain_ids value")
                    if self.auth.account.can_read_domain(d) or \
                        self.auth.account.in_global_acl_emails(
                            self.auth.account.email
                            ):

                        domain_id_list.append(d)
            else:
                for d in requested_domain_ids:
                    if not str.isdigit(str(d)):
                        abort(400, message="invalid domain_ids value")
                domain_id_list = requested_domain_ids
        else:
            # only build list for non-senior_admin users
            if self.auth.account.account_type != "senior_admin":
                for d in self.auth.account.domains:
                    domain_id_list.append(d)

        # get audit logs
        total_logs = 0
        if self.auth.account.account_type == "senior_admin" or \
            self.auth.account.in_global_acl_emails(
                self.auth.account.email
                ):

            if len(domain_id_list) == 0:
                logs = ModelAuditLog.select().where(
                    ModelAuditLog.entry ** ('%' + search + '%')
                )
            else:
                logs = ModelAuditLog.select().where(
                    ModelAuditLog.domain_id << domain_id_list,
                    ModelAuditLog.entry ** ('%' + search + '%')
                )

            total_logs = logs.count()
            logs = self.paginate_query(logs, request.args)
            logs = self.sort_query(logs, request.args)
        else:
            if len(domain_id_list) > 0:
                logs = ModelAuditLog.select().where(
                    ModelAuditLog.domain_id << domain_id_list,
                    ModelAuditLog.entry ** ('%' + search + '%')
                )

                total_logs = logs.count()
                logs = self.paginate_query(logs, request.args)
                logs = self.sort_query(logs, request.args)
            else:
                logs = []

        audit_logs = []
        for l in logs:
            audit_logs.append(l.to_clean_dict())

        return {
            'status': 'ok',
            'audit_logs': audit_logs,
            'total_audit_logs': total_logs
        }
