# -*- coding: utf-8 -*-
"""Django settings for CAPCollector project."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from distutils.version import StrictVersion
import os
import sys

import django
from sensitive import *
from settings_prod import *


###### Default settings (only modify for advanced configuration) ######

SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN

CAP_SCHEMA_FILE = "cap1.2.xsd"
CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"
CERT_NS = "http://www.w3.org/2000/09/xmldsig#"

VERSION = "CAPCollector v1.0"

EMAIL_SUBJECT_PREFIX = ""

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Your keys and certificates.
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")

# Schema files directory.
SCHEMA_DIR = os.path.join(BASE_DIR, "schema")

# Group name for persons allowed to release alerts.
# A User entry must exist for a given person to access the application.
# Users who will release alerts to the public must additionally be in this group.
# See https://docs.djangoproject.com/en/dev/topics/auth/ for managing Users.
ALERT_CREATORS_GROUP_NAME = "can release alerts"


###### Django framework settings (only modify for advanced configuration) ######

# A list of strings representing the host/domain names that this Django site ca
# serve.
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [SITE_DOMAIN]

# Must be set to False in production.
# See https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = False

# List of locations of the template source files searched by Django loaders.
# See https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

# A tuple of strings designating all applications that are enabled in this
# Django installation.
# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
)

# A tuple of middleware classes to use.
# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MIDDLEWARE_CLASSES
# Per https://github.com/mozilla/django-session-csrf
# session_csrf.CsrfMiddleware must be listed after AuthenticationMiddleware.
MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.ErrorLogMiddleware",
    "session_csrf.CsrfMiddleware",
)

# Set up session csrf in context processor.
# For Django version 1.8 or above, update TEMPLATES OPTIONS section with
# session csrf context processor.
# For Django version less than 1.8, update TEMPLATE_CONTEXT_PROCESSORS.
if StrictVersion(django.get_version()) >= StrictVersion("1.8"):
  # see https://docs.djangoproject.com/en/dev/ref/settings/#templates
  TEMPLATES = [
      {
          "BACKEND": "django.template.backends.django.DjangoTemplates",
          "DIRS": [
              "templates",
          ],
          "APP_DIRS": True,
          "OPTIONS": {
              "context_processors": [
                  "django.contrib.auth.context_processors.auth",
                  "django.template.context_processors.debug",
                  "django.template.context_processors.i18n",
                  "django.template.context_processors.media",
                  "django.template.context_processors.static",
                  "django.template.context_processors.tz",
                  "django.contrib.messages.context_processors.messages",
                  "session_csrf.context_processor",
              ],
          },
      },
  ]
else:
  # see https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
  TEMPLATE_CONTEXT_PROCESSORS = (
      "django.contrib.auth.context_processors.auth",
      "django.core.context_processors.debug",
      "django.core.context_processors.i18n",
      "django.core.context_processors.media",
      "django.core.context_processors.static",
      "django.core.context_processors.tz",
      "django.contrib.messages.context_processors.messages",
      "session_csrf.context_processor",
  )

# A string representing the full Python import path to your root URLconf.
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "CAPCollector.urls"

# The full Python path of the WSGI application object that Django’s built-in
# servers (e.g. runserver) will use
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "CAPCollector.wsgi.application"

# Paths to translation files.
# See https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths.
LOCALE_PATHS = (
    os.path.join(BASE_DIR, "conf/locale"),
)

# Set to False if you don't need translation support.
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-USE_I18N
USE_I18N = True

# Localizes data formatting.
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# A boolean that specifies if datetimes will be timezone-aware by default or not
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# URL to use when referring to static files.
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/client/"

# The absolute path to the directory where collectstatic will collect static
# files for deployment.
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.join(BASE_DIR, "client")

# This setting defines the additional staticfiles locations.
# https://docs.djangoproject.com/en/dev/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# The URL where requests are redirected for login.
LOGIN_URL = "/login/"

# The URL where requests are redirected after login.
LOGIN_REDIRECT_URL = "/"

# Helper variable indicating test environment.
TESTING = "test" in sys.argv

if os.environ.get("SERVER_SOFTWARE"):
  # On appengine, we need to use a custom email backend
  EMAIL_BACKEND = "CAPCollector.appengine_mail.EmailBackend"

# Import development environment settings if needed.
# Export CAP_TOOLS_DEV=1 environment variable to include dev settings.
# AppEngine development environment includes dev settings automatically.
if (os.environ.get("CAP_TOOLS_DEV") or
    (os.environ.get("SERVER_SOFTWARE") and
     os.environ.get("SERVER_SOFTWARE").startswith("Development"))):
  from settings_dev import *
if TESTING:
  from settings_test import *
  INSTALLED_APPS += ("tests",)
