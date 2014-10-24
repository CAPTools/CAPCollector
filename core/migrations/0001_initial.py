"""Initial migration for CAPCollector application.

See https://docs.djangoproject.com/en/dev/topics/migrations/#data-migrations.
"""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"

from django.contrib.auth.models import Group
from django.db import migrations


def CreateGroups(unused_apps, unused_schema_editor):
    group_obj = Group()
    group_obj.name = "can release alerts"
    group_obj.save()


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(CreateGroups),
    ]
