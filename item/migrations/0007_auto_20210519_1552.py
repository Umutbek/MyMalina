# Generated by Django 3.1 on 2021-05-19 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0006_modelcart_modelpostcart'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modelcart',
            old_name='client',
            new_name='clientid',
        ),
        migrations.RenameField(
            model_name='modelcart',
            old_name='store',
            new_name='storeid',
        ),
    ]
