"""Django settings for CAPCollector project test environment."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Relative path to your active/inactive alerts directories.
ACTIVE_ALERTS_DATA_DIR = os.path.join(BASE_DIR, "testdata/alerts/active")
GOLDEN_ALERTS_DATA_DIR = os.path.join(BASE_DIR, "testdata/alerts/golden")
INACTIVE_ALERTS_DATA_DIR = os.path.join(BASE_DIR, "testdata/alerts/inactive")
TEMPLATES_DIR = os.path.join(BASE_DIR, "client/templates")
TEMPLATES_TESTDATA_DIR = os.path.join(BASE_DIR, "testdata/templates")

CREDENTIALS_DIR = os.path.join(BASE_DIR, "testdata/credentials")

SITE_SCHEME = "http"
SITE_DOMAIN = "myagency.gov"
SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN
