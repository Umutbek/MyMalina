# Generated by Django 3.1 on 2021-06-30 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0035_modelcart_visibility'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelorder',
            name='reference1',
        ),
        migrations.RemoveField(
            model_name='modelorder',
            name='reference2',
        ),
        migrations.DeleteModel(
            name='ClientOrderItem',
        ),
    ]
