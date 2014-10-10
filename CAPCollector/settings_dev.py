"""Django settings for CAPCollector project dev environment."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import socket

DEBUG = True
TEMPLATE_DEBUG = True

# Set your site name here.
SITE_DOMAIN = socket.gethostname()
SITE_SCHEME = "http"
SITE_PORT = "9090"  # Optional.
SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN

ALLOWED_HOSTS = [SITE_DOMAIN]

if SITE_PORT:
  SITE_URL = SITE_URL + ":" + SITE_PORT
