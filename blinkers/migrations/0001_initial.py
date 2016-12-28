# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-27 13:49
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.migrations.operations.models import CreateModel


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
          """
          --
          -- Create model NewHope
          --
          CREATE TABLE "blinkers_newhope" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            "xml" text NOT NULL, 
            "title" varchar(100) GENERATED ALWAYS AS (extractvalue(`xml`,'/article/title')) STORED 
          );
          """,
          reverse_sql="BEGIN; DROP TABLE `blinkers_newhope`; COMMIT",
          state_operations=[CreateModel(
            name='NewHope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xml', models.TextField()),
                ('title', models.CharField(max_length=100)),
            ],)]
        ),
    ]
