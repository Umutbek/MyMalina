# Generated by Django 3.1 on 2021-05-15 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_regularaccount_firebase_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='regularaccount',
            name='code',
        ),
    ]
