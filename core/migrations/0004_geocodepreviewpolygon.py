# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alert_updated'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeocodePreviewPolygon',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, verbose_name=b'ID', primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('last_modified_at', models.DateTimeField(auto_now=True, verbose_name='Last modification time')),
                ('content', models.TextField(verbose_name='Polygons')),
            ],
            options={
                'verbose_name': 'Geocode Preview Polygon',
                'verbose_name_plural': 'Geocode Preview Polygon',
            },
        ),
    ]
