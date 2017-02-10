#!/usr/bin/env python
"""
config.py - configures vegadns2 from the environment variables
"""
import os
import sys

import pystache
from netaddr import IPSet


def pem_is_valid(pem):
    if pem:
        lines = pem.split('\n')
        return (len(lines) > 2
            and "-----BEGIN CERTIFICATE-----" in lines[0]
            and "-----END CERTIFICATE-----" in lines[-1])
        print >> sys.stderr, "SECRET_DB_CA_CERT env variable contains invalid MySQL CA certficate PEM"
    return False

directory = os.path.dirname(os.path.realpath(__file__))
def main():
    db_ssl_ca_cert = os.getenv("SECRET_DB_CA_CERT")
    db_ssl_ca_file = os.getenv("DB_CA_FILE")

    if pem_is_valid(db_ssl_ca_cert) and db_ssl_ca_file:
        try:
            with open(db_ssl_ca_file, 'w') as f:
                f.write(db_ssl_ca_cert)
        except Exception as err:
            print >> sys.stderr, "Problem writing MySQL CA certficate file", err
            sys.exit(1)
    else:
        # Reset db_ssl_ca_file if we're missing one or more environment variables for SSL
        # to avoid adding an empty 'ssl_ca' option to the local.ini config.
        if not db_ssl_ca_file:
            print >> sys.stderr, "DB_CA_FILE env variable undefined, skipping MySQL SSL config."
        if not db_ssl_ca_cert:
            print >> sys.stderr, "SECRET_DB_CA_CERT env variable undefined, skipping MySQL SSL config."
            db_ssl_ca_file = None

    # Verify that we can parse the TRUSTED_IPS list
    trusted_ips = os.getenv("TRUSTED_IPS", default="127.0.0.1")
    trusted_ips = "".join(trusted_ips.split()) # remove whitespace
    trusted_list = trusted_ips.split(',')

    try:
        trusted_ip_range = IPSet(trusted_list)
    except Exception as e:
        print >> sys.stderr, trusted_list, e
        print >> sys.stderr, "Problem parsing TRUSTED_IPS environment variable"
        sys.exit(1)

    try:
        config = {
            "db_host": os.getenv("DB_HOST", default="localhost"),
            "db_user": os.getenv("DB_USER", default="vegadns"),
            "db_pass": os.getenv("SECRET_DB_PASS", default="secret"),
            "db_db": os.getenv("DB_DB", default="vegadns"),
            "db_ssl_ca": db_ssl_ca_file,
            "vegadns_generation": os.getenv("VEGADNS_GENERATION", default=""),
            "vegadns": os.getenv("VEGADNS", default="http://127.0.0.1/1.0/export/tinydns"),
            "trusted_ips": trusted_ips,
            "ui_url": os.getenv("UI_URL", default="http://localhost:8080"),
            "email_method": os.getenv("EMAIL_METHOD", default="smtp"),
            "smtp_host": os.getenv("SMTP_HOST", default="localhost"),
            "smtp_port": os.getenv("SMTP_PORT", default="25"),
            "smtp_auth": os.getenv("SMTP_AUTH", default="false"),
            "smtp_user": os.getenv("SMTP_USER", default=""),
            "smtp_password": os.getenv("SECRET_SMTP_PASSWORD", default=""),
            "support_name": os.getenv("SUPPORT_NAME", default="The VegaDNS Team"),
            "support_email": os.getenv("SUPPORT_EMAIL", default="support@example.com"),
            "acl_labels": os.getenv("ACL_LABELS", default=""),
            "acl_emails": os.getenv("ACL_EMAILS", default=""),
            "enable_redis_notifications": os.getenv("ENABLE_REDIS_NOTIFICATIONS", default="false"),
            "redis_host": os.getenv("REDIS_HOST", default="127.0.0.1"),
            "redis_port": os.getenv("REDIS_PORT", default="6379"),
            "redis_channel": os.getenv("REDIS_CHANNEL", default="VEGADNS-CHANGES")
        }
    except Exception as err:
        print >> sys.stderr, "Problem reading environment", err
        sys.exit(1)

    # optionally use first argument as template, path is still
    # relative to this script
    template_file = "./local.ini.template"
    if len(sys.argv) > 1:
        template_file = sys.argv[1]

    try:
        with open(directory + "/" + template_file) as template:
            print pystache.render(template.read(), config)
    except Exception as err:
        print >> sys.stderr, "Problem rendering template", err
        sys.exit(1)


if __name__ == "__main__":
    main()
