from django.db import models


class OrderStatuses(models.IntegerChoices):
    New = 1, 'Новый'
    Packing = 2, 'Подтвержден'
    Rejected = 3, 'Отменен'
    Ready = 4, 'Готово'
    Delivering = 5, 'В пути'
    Received = 6, 'Получен'
    Arrived = 7, 'Прибыл'
    Delivered = 8, 'Доставлено'
    Refuse = 9, 'Отказ клиента'


class OrderType(models.IntegerChoices):
    delivery = 1, 'Доставка'
    pickup = 2, 'Самовывоз'


class PaymentType(models.IntegerChoices):
    cash = 1, 'Наличка'
    paybox = 2, 'Пейбокс'
    

