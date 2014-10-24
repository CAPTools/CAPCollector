# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=36, verbose_name='Alert UUID', db_index=True)),
                ('created_at', models.DateTimeField(verbose_name='Alert creation time', db_index=True)),
                ('expires_at', models.DateTimeField(verbose_name='Alert expiration time', db_index=True)),
                ('content', models.TextField(verbose_name='Alert content')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AreaTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Template Title')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Template creation time')),
                ('last_modified_at', models.DateTimeField(auto_now=True, verbose_name='Template last modification time')),
                ('content', models.TextField(verbose_name='Template Content')),
            ],
            options={
                'verbose_name': 'Area Template',
                'verbose_name_plural': 'Area Templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Template Title')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Template creation time')),
                ('last_modified_at', models.DateTimeField(auto_now=True, verbose_name='Template last modification time')),
                ('content', models.TextField(verbose_name='Template Content')),
            ],
            options={
                'verbose_name': 'Message Template',
                'verbose_name_plural': 'Message Templates',
            },
            bases=(models.Model,),
        ),
    ]
