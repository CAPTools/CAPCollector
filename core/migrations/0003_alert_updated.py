# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alert_areatemplate_messagetemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='updated',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Alert replaced by an update or cancel'),
            preserve_default=True,
        ),
    ]
