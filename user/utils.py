from django.db import models

class UserTypes(models.IntegerChoices):
    USER = 1, 'Пользователь'
    STORE = 2, 'МАГАЗИН'
    Admin = 3, 'Админ'


class UserGender(models.IntegerChoices):
    Male = 1, 'Мужской'
    Female =2, 'Женский'
    Other = 3, 'Другое'
    NotIndicated = 4, 'Не указано'

class OrderStatuses(models.IntegerChoices):
    New = 1, 'Новый'
    Packing = 2, 'Упаковывается'
    Delivering = 3, 'В пути'
    Delivered = 4, 'Доставлено'
    Rejected = 5, 'Отказано'


class Prompt(models.IntegerChoices):
    PAYMENTMETHOD = 1, 'Способ оплаты'
    DELIVERY = 2, 'Способ доставки'
    USERAGREEMENT = 3, 'Пользовательское соглашение'
    OFFER = 4, 'Оферта'
    APP = 5, 'О приложении'
    FORBUSINESS = 6, 'Для бизнеса'