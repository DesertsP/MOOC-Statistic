# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 06:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mooc', '0005_auto_20161005_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='chinese_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='url',
            field=models.CharField(max_length=511),
        ),
    ]
