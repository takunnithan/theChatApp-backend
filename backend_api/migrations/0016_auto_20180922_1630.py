# Generated by Django 2.0.6 on 2018-09-22 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_api', '0015_usersession'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersession',
            name='id',
        ),
        migrations.AlterField(
            model_name='usersession',
            name='user_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]