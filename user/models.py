from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)

from user import utils
from django_fsm import FSMIntegerField, transition

from django.utils.translation import ugettext_lazy as _
from rest_framework.reverse import reverse


class Category(models.Model):
    """Category model"""
    name = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=1000, null=True, blank=True)
    available = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Subcategory model"""
    name = models.CharField(max_length=200, null=True)
    icon = models.CharField(max_length=1000, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Manager for user profiles"""
    def create_user(self, login, password=None, **extra_fields):
        """Creates and saves a new user"""

        if not login:
            raise ValueError('User must have a login')

        if not password:
            raise ValueError('User must have a password')

        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password):
        """Create a superuser"""
        user = self.create_user(login, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=200, null=True, blank=True)
    login = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    type = FSMIntegerField(choices=utils.UserTypes.choices, default=utils.UserTypes.USER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'login'

    class Meta:
        ordering = ('-id',)
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")


class RegularAccount(User):
    """Model for Regular account"""
    surname = models.CharField(max_length=200, null=True, blank=True)
    datebirth = models.DateField(null=True, blank=True, verbose_name="День рождение")
    gender = FSMIntegerField(choices=utils.UserGender.choices, default=utils.UserGender.NotIndicated, verbose_name="Пол")
    score = models.PositiveIntegerField(default=0, verbose_name="Баллы")
    device_id = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = _("Обычный пользователь")
        verbose_name_plural = _("Обычные пользователи")

    @property
    def code(self):
        return self.id * 11111


class Store(User):
    """Model for Store"""
    percentage = models.FloatField(default=0, verbose_name="Процент")
    storeaddress = models.JSONField(null=True, blank=True)
    deliverycost = models.IntegerField(default=0, verbose_name="Цена службы доставки")
    worktime = models.CharField(max_length=200, null=True, blank=True, verbose_name="Время работы")
    telegram = models.CharField(max_length=200, null=True, blank=True)
    whatsapp = models.CharField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=200, null=True, blank=True)
    slogan = models.CharField(max_length=200, null=True, blank=True, verbose_name="Слоган")
    avgcheck = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")

    def get_url(self):
        return reverse('user:stores-detail', kwargs={'pk': self.pk})


class UserFavouriteStore(models.Model):
    """Model for user favouirite stores"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client', null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='fav_store')


class WithDrawScore(models.Model):
    """Withdraw user score manually"""
    client = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, related_name='appclient', null=True)
    score = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, null=True)


class RatingStar(models.Model):
    """Звезда рейтинга"""
    value = models.SmallIntegerField("Значение", default=0)

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"
        ordering = ["-value"]


class Rating(models.Model):
    """Рейтинг"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="author")
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name="звезда")
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="Магазины"
    )

    def __str__(self):
        return f"{self.star} - {self.store}"

    text = models.TextField("Сообщение", max_length=5000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"


class AppPrompt(models.Model):
    type = FSMIntegerField(choices=utils.Prompt.choices)
    text = models.TextField(null=True, blank=True)