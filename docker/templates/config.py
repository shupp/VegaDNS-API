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
        }
    except Exception as err:
        print "Problem reading environment", err
        sys.exit(1)

    try:
        with open(directory + "/local.ini.template") as template:
            print pystache.render(template.read(), config)
    except Exception as err:
        print "Problem rendering template", err
        sys.exit(1)


if __name__ == "__main__":
    main()
