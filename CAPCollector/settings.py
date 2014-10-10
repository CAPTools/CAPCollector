# -*- coding: utf-8 -*-
"""Django settings for CAPCollector project."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

import os
import sys
from sensitive import *


###### Standard configuration.  You need to set these variables.  ######

# Change to https if your site uses https.
SITE_SCHEME = "http"

# Change to the URL where users will find this app.
SITE_DOMAIN = "myagency.gov"

# A string representing the time zone for this installation.
# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = "US/Central"

# Default language.
# See https://docs.djangoproject.com/en/dev/ref/settings/#language-code.
LANGUAGE_CODE = "en"

# Add new languages here.
# See https://docs.djangoproject.com/en/dev/ref/settings/#languages.
# TODO(arcadiy): figure out a way to support CAP info language format (RFC 3066)
# Django seems to treat fr-CA as just fr
LANGUAGES = (
    ("en", "English"),
    ("hi", "हिंदी"),
    ("pt", "Português"),
)

###### Default settings (only modify for advanced configuration) ######

SITE_URL = SITE_SCHEME + "://" + SITE_DOMAIN

CAP_SCHEMA_FILE = "cap1.2.xsd"
CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"
CERT_NS = "http://www.w3.org/2000/09/xmldsig#"

VERSION = "CAPCollector v1.0"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "alerts")

# Your keys and certificates.
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")

# Schema files directory.
SCHEMA_DIR = os.path.join(BASE_DIR, "schema")

# Group name for persons allowed to create new alerts.
# A User entry must exist for a given person to access the application.
# Users who will post new alerts must additionally be in this group.
# See https://docs.djangoproject.com/en/dev/topics/auth/ for managing Users.
ALERT_CREATORS_GROUP_NAME = "creators"


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
    "tests",
)

# A tuple of middleware classes to use.
# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# A string representing the full Python import path to your root URLconf.
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "CAPCollector.urls"

# The full Python path of the WSGI application object that Django’s built-in
# servers (e.g. runserver) will use
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "CAPCollector.wsgi.application"

# A dictionary containing the settings for all databases to be used with Django.
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

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

# Import development environment settings if needed.
if os.environ.get("CAPTOOLS_DEV"):
  from settings_dev import *
elif TESTING:
  from settings_test import *


