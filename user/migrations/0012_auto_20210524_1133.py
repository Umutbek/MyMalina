# Generated by Django 3.1 on 2021-05-24 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_regularaccount_device_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='deliverycost',
            field=models.IntegerField(default=0, verbose_name='Цена службы доставки'),
        ),
    ]
