"""WSGI config for CAPCollector project.

It exposes the WSGI callable as a module-level variable named "application".

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

# AppEngine third-party apps path include.
if "SERVER_SOFTWARE" in os.environ:
  if os.environ.get("SERVER_SOFTWARE"):  # AppEngine.
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "libs"))
  else:  # AppEngine managed VMs.
    sys.path.insert(0, "/usr/local/lib/python2.7/dist-packages/")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CAPCollector.settings")
application = get_wsgi_application()
