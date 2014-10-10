"""CAP Collector models admin."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"


from core import models
from django.contrib import admin

admin.site.register(models.Alert)
