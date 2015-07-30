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
