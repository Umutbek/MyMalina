# Generated by Django 3.1 on 2021-06-24 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_rating_ratingstar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Help',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentmethod', models.TextField(blank=True, null=True)),
                ('delivery', models.TextField(blank=True, null=True)),
                ('useragreement', models.TextField(blank=True, null=True)),
                ('help', models.TextField(blank=True, null=True)),
                ('offer', models.TextField(blank=True, null=True)),
                ('app', models.TextField(blank=True, null=True)),
                ('forbusiness', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
