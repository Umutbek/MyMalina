# Generated by Django 3.1 on 2021-10-11 22:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('login', models.CharField(max_length=200, unique=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('avatar', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=200, null=True)),
                ('type', django_fsm.FSMIntegerField(choices=[(1, 'Пользователь'), (2, 'МАГАЗИН'), (3, 'Админ')], default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='AppPrompt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', django_fsm.FSMIntegerField(choices=[(1, 'Способ оплаты'), (2, 'Способ доставки'), (3, 'Пользовательское соглашение'), (4, 'Оферта'), (5, 'О приложении'), (6, 'Для бизнеса')])),
                ('text', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('icon', models.CharField(blank=True, max_length=1000, null=True)),
                ('available', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RatingStar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(default=0, verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Звезда рейтинга',
                'verbose_name_plural': 'Звезды рейтинга',
                'ordering': ['-value'],
            },
        ),
        migrations.CreateModel(
            name='RegularAccount',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='user.user')),
                ('surname', models.CharField(blank=True, max_length=200, null=True)),
                ('datebirth', models.DateField(blank=True, null=True, verbose_name='День рождение')),
                ('gender', django_fsm.FSMIntegerField(choices=[(1, 'Мужской'), (2, 'Женский'), (3, 'Другое'), (4, 'Не указано')], default=4, verbose_name='Пол')),
                ('score', models.IntegerField(default=0, verbose_name='Баллы')),
                ('device_id', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'Обычный пользователь',
                'verbose_name_plural': 'Обычные пользователи',
            },
            bases=('user.user',),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='user.user')),
                ('percentage', models.FloatField(default=0, verbose_name='Процент')),
                ('storeaddress', models.JSONField(blank=True, null=True)),
                ('deliverycost', models.IntegerField(default=0, verbose_name='Цена службы доставки')),
                ('worktime', models.CharField(blank=True, max_length=200, null=True, verbose_name='Время работы')),
                ('telegram', models.CharField(blank=True, max_length=200, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=200, null=True)),
                ('instagram', models.CharField(blank=True, max_length=200, null=True)),
                ('slogan', models.CharField(blank=True, max_length=200, null=True, verbose_name='Слоган')),
                ('avgcheck', models.FloatField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.category')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
            },
            bases=('user.user',),
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('icon', models.CharField(blank=True, max_length=1000, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.category')),
            ],
        ),
        migrations.CreateModel(
            name='WithDrawScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appclient', to='user.regularaccount')),
            ],
        ),
        migrations.CreateModel(
            name='UserFavouriteStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fav_store', to='user.store')),
            ],
        ),
        migrations.AddField(
            model_name='store',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.subcategory'),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, max_length=5000, null=True, verbose_name='Сообщение')),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('star', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.ratingstar', verbose_name='звезда')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='user.store', verbose_name='Магазины')),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
            },
        ),
    ]
