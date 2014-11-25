"""Django settings for CAPCollector project dev environment."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os
import socket

from sensitive import *

DEBUG = True
TEMPLATE_DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Set your site name here.
SITE_DOMAIN = socket.gethostname()
SITE_SCHEME = "http"
SITE_PORT = "9090"  # Optional.
SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN

ALLOWED_HOSTS = [SITE_DOMAIN]

if SITE_PORT:
  SITE_URL = SITE_URL + ":" + SITE_PORT

# print all outgoing email to the console during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Default database settings.
# Running in development, but want to access production database.
if os.environ.get("CAP_TOOLS_DB") == "prod":
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.mysql",
          "HOST": PROD_FROM_DEV_DATABASE_HOST,
          "NAME": PROD_FROM_DEV_DATABASE_NAME,
          "USER": PROD_FROM_DEV_DATABASE_USER,
          "PASSWORD": PROD_FROM_DEV_DATABASE_PASSWORD,
      }
  }
# For AppEngine development environment.
elif (os.environ.get("CAP_TOOLS_DB") == "dev" or
      (os.environ.get("SERVER_SOFTWARE") and
       os.environ.get("SERVER_SOFTWARE").startswith("Development"))):
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.mysql",
          "HOST": DEV_DATABASE_HOST,
          "NAME": DEV_DATABASE_NAME,
          "USER": DEV_DATABASE_USER,
          "PASSWORD": DEV_DATABASE_PASSWORD,
      },
  }
# For regular setup.
else:
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.sqlite3",
          "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
      }
  }

# Dummy secret key for development environment.
SECRET_KEY = "@l@24ziuxky!8sh+yiq5ot#d^d4fqyxe$f39f@(ye183lq#hkf"
