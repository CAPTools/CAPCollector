# -*- coding: utf-8 -*-
"""Django settings for CAPCollector project test environment."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CREDENTIALS_DIR = os.path.join(BASE_DIR, "testdata/credentials")

SITE_SCHEME = "http"
SITE_DOMAIN = "localhost"
SITE_PORT = "8081"
SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN + ":" + SITE_PORT

ALLOWED_HOSTS = [SITE_DOMAIN]

LANGUAGES = (
    ("en-us", "English"),
    ("hi", "Hindi"),
    ("pt-br", "Portugues"),
)

# Dummy secret key for testing environment.
SECRET_KEY = "@l@24ziuxky!8sh+yiq5ot#d^d4fqyxe$f39f@(ye183lq#hkf"
