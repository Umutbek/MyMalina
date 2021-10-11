from django.db import models
from user.models import Store, RegularAccount, User, RatingStar
from item import utils, firestore

from django_fsm import FSMIntegerField, transition
from pyfcm import FCMNotification
import requests
from rest_framework.reverse import reverse


class ItemCategory(models.Model):
    name = models.CharField(max_length=200)
    supplier = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    itemcategory = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=200, null=True)
    cost = models.FloatField()
    sostav = models.TextField(null=True, blank=True)
    gram = models.FloatField(null=True, blank=True)
    ccal = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    fats = models.FloatField(null=True, blank=True)
    carbo = models.FloatField(null=True, blank=True)
    costsale = models.FloatField(default=0)
    taketogether = models.ManyToManyField('self')
    supplier = models.ForeignKey(Store, on_delete=models.CASCADE)

    @property
    def additive(self):
        return self.itemadditive_set.all()

    @property
    def images(self):
        return self.itemimages_set.all()

    @property
    def salecost(self):

        return self.cost - ((self.cost*self.costsale)/100)


    def get_url(self):
        return reverse('item:items-detail', kwargs={'pk': self.pk})


class ItemAdditive(models.Model):
    """Model for additive items"""
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    cost = models.FloatField(default=0)


class ItemImages(models.Model):
    """Models for images"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    image = models.TextField(null=True)

    def __str__(self):
        return self.image


class UserFavouriteItems(models.Model):
    """Model for user favouirite items"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='fav_items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user")


class ItemWithQuantity(models.Model):
    """Item with quantity in cart"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="users_item")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    addedadditives = models.ManyToManyField('ItemAdditive')
    quantity = models.IntegerField(default=1)
    total = models.IntegerField(default=0)
    visibility = models.BooleanField(default=True)

    @property
    def totaladditiveprice(self):
        queryset = self.addedadditives.all().aggregate(
            totaladditiveprice=models.Sum('cost'))
        return queryset['totaladditiveprice']

    def save(self):
        self.total=self.item.cost * self.quantity
        super(ItemWithQuantity, self).save()


class ModelCart(models.Model):
    """Model for cart"""
    listitem = models.ManyToManyField('ItemWithQuantity')
    clientid = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, null=True, related_name="usercart")
    storeid = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, related_name="storecart")
    check = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    visibility = models.BooleanField(default=True)

    @property
    def totalprice(self):
        queryset = self.listitem.all().aggregate(
            totalprice=models.Sum('total'))
        return queryset['totalprice']

    @property
    def countcart(self):
        return self.listitem.count()


class RemoveItem(models.Model):
    """Model remove item from cart"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, related_name='removeitem')
    cart = models.ForeignKey(ModelCart, on_delete=models.CASCADE, null=True)


class Address(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    numhouse = models.CharField(max_length=200, null=True, blank=True)
    entrance = models.CharField(max_length=200, null=True, blank=True)
    floor = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200)
    location = models.CharField(max_length=200, null=True, blank=True)
    longitude = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.CharField(max_length=200, null=True, blank=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class ModelOrder(models.Model):
    """Model for client order"""
    clientId = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, related_name="clientId", null=True, blank=True)
    storeId = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="storeId")
    paymentType = FSMIntegerField(choices=utils.PaymentType.choices, default=utils.PaymentType.cash)
    paymentStatus = models.BooleanField(default=False)
    status = FSMIntegerField(choices=utils.OrderStatuses.choices, default=utils.OrderStatuses.New)
    iscourier = models.BooleanField(default=False)
    timedelivery = models.CharField(max_length=200, null=True, blank=True)
    quantityappliances = models.FloatField(null=True, blank=True)
    ordertype = FSMIntegerField(choices=utils.OrderType.choices, default=utils.OrderType.delivery)
    scancode = models.IntegerField(null=True, blank=True)
    count = models.IntegerField(default=0)
    declinereason = models.CharField(max_length=200, null=True, blank=True)
    refusereason = models.CharField(max_length=200, null=True, blank=True)

    scorepaid = models.IntegerField(default=0)
    scoregot = models.IntegerField(default=0)
    address = models.JSONField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    cart = models.ForeignKey(ModelCart, on_delete=models.SET_NULL, null=True, blank=True)
    reporttotal = models.IntegerField(default=0)

    @property
    def totalprice(self):
        queryset = self.cart.listitem.all().aggregate(
            totalprice=models.Sum('total'))
        return queryset['totalprice']

    @property
    def totalcount(self):
        queryset = self.cart.listitem.all().aggregate(
            totalcount=models.Sum('quantity'))
        return queryset['totalcount']

    def save(self, *args, **kwargs):

        if self.status == 2:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 2, "scorepaid": self.scorepaid})
            if self.ordertype == 10:
                url = "https://admin-porter.smartpost.kg/api/v1/order/create/for/malina/"
                if self.paymentType == 1:
                    data = {'login': 'Malina', 'password': 'pa1DPYFWmeowqHniqFz2syTwV0Ahhy',
                            'description': self.comment, 'address_from': self.storeId.storeaddress,
                            'address_to': self.address["name"], 'customer_amount': self.totalprice,
                            'customer_name': self.storeId.name, 'customer_phone': self.storeId.phone,
                            'receiver_name': self.clientId.name, 'receiver_phone': self.clientId.phone,
                            "pays_receiver": True, "partner_order_id": self.id
                            }
                else:
                    data = {'login': 'Malina', 'password': 'pa1DPYFWmeowqHniqFz2syTwV0Ahhy',
                            'description': self.comment, 'address_from': self.storeId.storeaddress,
                            'address_to': self.address["name"], 'customer_amount': self.totalprice,
                            'customer_name': self.storeId.name, 'customer_phone': self.storeId.phone,
                            'receiver_name': self.clientId.name, 'receiver_phone': self.clientId.phone,
                            "pays_receiver": False, "partner_order_id": self.id
                            }
                r = requests.post(url, json=data)

            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Ваш заказ готовится'
                send_notification(device_id, title, body)

        elif self.status == 3:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 3, "declinereason": self.declinereason})
            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Заказ отменен'
                send_notification(device_id, title, body)

        elif self.status == 4:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 4})
            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Ваш заказ готов'
                send_notification(device_id,title,body)

        elif self.status == 5:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 5})
            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Ваш заказ в пути'
                send_notification(device_id,title,body)

        elif self.status == 6:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 6})
            score = ((self.totalprice - self.storeId.deliverycost - self.scorepaid) * self.storeId.percentage)/100
            if self.scoregot<=0:
                self.clientId.score = self.clientId.score + score
                self.clientId.save()
            self.scoregot = score

            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Заказ получен'
                send_notification(device_id, title, body)

        elif self.status == 7:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 7})
            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Курьер на месте'
                send_notification(device_id,title,body)

        elif self.status == 8:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 8})
            score = ((self.totalprice - self.storeId.deliverycost - self.scorepaid) * self.storeId.percentage)/100
            if self.scoregot<=0:
                self.clientId.score = self.clientId.score + score
                self.clientId.save()
            self.scoregot = score

            device_id = self.clientId.device_id
            save_score_action(self.clientId, self.storeId, self, self.scoregot, self.scorepaid)

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Ваш заказ доставлено'
                send_notification(device_id, title, body)

        elif self.status == 9:
            firestore.db.collection(u'stores').document(str(self.storeId.id)).collection(u'orders').document(str(self.id)).update({"status": 9, "refusereason": self.refusereason})
            device_id = self.clientId.device_id

            if device_id:
                title = "Уведомление о вашем заказе"
                body = 'Заказ отказано'
                send_notification(device_id,title,body)
        super(ModelOrder, self).save(*args, **kwargs)


class OrderReview(models.Model):
    """Отзывы"""
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name="звезда")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, null=True, related_name="author_review")
    text = models.TextField("Сообщение", max_length=5000)
    date = models.DateTimeField(auto_now_add=True, null=True)
    order = models.ForeignKey(ModelOrder, on_delete=models.CASCADE, related_name="reviews", null=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class SaveOrderActions(models.Model):
    """Save every order actions"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="savestore")
    order = models.ForeignKey(ModelOrder, on_delete=models.CASCADE, null=True, related_name="saveorder")
    prev_status = models.IntegerField(null=True, blank=True)
    status = models.IntegerField()
    changedby = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, related_name="saveuser")


class ScoreActions(models.Model):
    """Save every score paid, score added actions"""
    user = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, related_name="usersave")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="storesave")
    order = models.ForeignKey(ModelOrder, on_delete=models.CASCADE, null=True, related_name="ordersave")
    scoregot = models.IntegerField(null=True, blank=True)
    scorepaid = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)


class SavePaymentAction(models.Model):
    user = models.ForeignKey(RegularAccount, on_delete=models.CASCADE, related_name="user_payment_save")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="store_payment_save")
    order = models.ForeignKey(ModelOrder, on_delete=models.CASCADE, null=True, related_name="order_payment_save")
    paymentType = models.CharField(max_length=200)
    totalprice = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True, null=True)


class Report(models.Model):
    """Model for order report"""
    total = models.IntegerField(default=0)


def save_action(store, order, prev_status, status, changedby, user):
    action = SaveOrderActions(store=store, order=order, prev_status=prev_status, status=status, changedby=changedby, user=user)
    action.save()


def save_payment_action(user, store, order, paymentType, totalprice):
    payment_action = SavePaymentAction(user=user, store=store, order=order, paymentType=paymentType, totalprice=totalprice)
    payment_action.save()


def save_score_action(user, store, order,scoregot,scorepaid):
    score_action = ScoreActions.objects.filter(user=user, store=store, order=order).first()
    if score_action:
        score_action.scoregot = scoregot
        score_action.save()
    else:
        score_action = ScoreActions(user=user, store=store, order=order, scorepaid=scorepaid)
        score_action.save()


def send_notification(device_id, title, body):
    fcm = FCMNotification(api_key="AAAAZb7jhUg:APA91bHYanYczet9wNojIbQbIwp3dgxl2SI69jZF5hLhFuQ1ii2Cy0v1ZbkjkBc8khNg0KGVvy82lP4pZj8tnta3T1kF5DUI6SouzQCYiNCJILOuEiZjbOnuy3jLMuu2Jb6BkTlakMuZ")
    return fcm.notify_single_device(
        registration_id=device_id,
        message_title=title,
        message_body=body
    )

