# Generated by Django 3.1 on 2021-07-13 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_auto_20210713_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='storeaddress',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Адресс'),
        ),
    ]
