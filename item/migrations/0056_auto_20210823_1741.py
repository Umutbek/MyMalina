# Generated by Django 3.1 on 2021-08-23 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0055_itemwithquantity_visibility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemwithquantity',
            name='addedadditives',
            field=models.ManyToManyField(db_constraint=False, to='item.ItemAdditive'),
        ),
    ]
