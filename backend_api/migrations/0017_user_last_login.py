# Generated by Django 2.0.6 on 2018-09-22 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_api', '0016_auto_20180922_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]
