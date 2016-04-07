#!/usr/bin/env python
"""
config.py - configures vegadns2 from the environment variables
"""
import os
import sys

import pystache



directory = os.path.dirname(os.path.realpath(__file__))
def main():
    try:
        config = {
            "db_host": os.getenv("DB_HOST", default="localhost"),
            "db_user": os.getenv("DB_USER", default="vegadns"),
            "db_pass": os.getenv("SECRET_DB_PASS", default="secret"),
            "db_db": os.getenv("DB_DB", default="vegadns"),
            "vegadns_generation": os.getenv("VEGADNS_GENERATION", default=""),
            "vegadns": os.getenv("VEGADNS", default="http://127.0.0.1/1.0/export/tinydns"),
            "trusted_ips": os.getenv("TRUSTED_IPS", default="127.0.0.1"),
            "ui_url": os.getenv("UI_URL", default="http://localhost:8080"),
            "email_method": os.getenv("EMAIL_METHOD", default="smtp"),
            "smtp_host": os.getenv("SMTP_HOST", default="localhost"),
            "smtp_port": os.getenv("SMTP_PORT", default="25"),
            "smtp_auth": os.getenv("SMTP_AUTH", default="false"),
            "smtp_user": os.getenv("SMTP_USER", default=""),
            "smtp_password": os.getenv("SMTP_PASSWORD", default=""),
            "support_name": os.getenv("SUPPORT_NAME", default="The VegaDNS Team"),
            "support_email": os.getenv("SUPPORT_EMAIL", default="support@example.com"),
        }
    except Exception as err:
        print "Problem reading environment", err
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
        print "Problem rendering template", err
        sys.exit(1)


if __name__ == "__main__":
    main()
