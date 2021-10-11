# Generated by Django 3.1 on 2021-05-25 08:27

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20210524_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=django_fsm.FSMIntegerField(choices=[(1, 'Пользователь'), (2, 'МАГАЗИН'), (3, 'Админ')], default=1),
        ),
    ]
