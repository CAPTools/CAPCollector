"""CAPCollector project production settings."""
# -*- coding: utf-8 -*-
from sensitive import *

###### Standard configuration.  You need to set these variables.  ######

# Change to http at your own risk.
SITE_SCHEME = "https"

# Change to the URL where users will find this app.
# If you using Appengine, put <application_id>.appspot.com (e.g.
# cap-tools.appspot.com)
SITE_DOMAIN = "myagency.gov"

# A string representing the time zone for this installation.
# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = "US/Central"

# Default language.
# The exact code must also appear in LANGUAGES below.
# See https://docs.djangoproject.com/en/dev/ref/settings/#language-code.
LANGUAGE_CODE = "en-us"

# Add new languages here.
# The list is a tuple of two-tuples in the format (language code, language name)
# Both the language and the country parts of language code are lower case.
# The separator is a dash. Examples: it, de-at, es, pt-br.
# See https://docs.djangoproject.com/en/dev/ref/settings/#languages
# and https://docs.djangoproject.com/en/1.7/topics/i18n/#definitions for more
# information.
LANGUAGES = (
    ("en-us", "English"),
    ("hi", "हिंदी"),
    ("pt-br", "Português"),
)

# Set map default viewport here.
MAP_DEFAULT_VIEWPORT = {
    "center_lat": 37.422,
    "center_lon": -122.084,
    "zoom_level": 12,
}

# A dictionary containing the settings for all databases to be used with Django.
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# See https://cloud.google.com/appengine/docs/python/cloud-sql/django for
# Django on CloudSQL documentation.
# DATABASE_* variables should be defined in sensitive.py module.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": DATABASE_HOST,  # /cloudsql/... path or regular IP address.
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
    },
}

