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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": DATABASE_HOST,  # /cloudsql/... path or regular IP address.
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
    },
}
