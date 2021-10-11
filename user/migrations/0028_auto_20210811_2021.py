# Generated by Django 3.1 on 2021-08-11 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_auto_20210714_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rating',
            name='text',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Сообщение'),
        ),
    ]
