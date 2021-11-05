from user.models import RegularAccount, Store
from item import models, firestore
import xml.etree.ElementTree as ET
import hmac
import requests
import hashlib
from operator import attrgetter
from app import settings
from django.utils.crypto import get_random_string


def create_cart(self,serializer):

    itemid = serializer.validated_data['itemid']
    client = serializer.validated_data['client']
    store = serializer.validated_data['store']
    additives = serializer.validated_data['additives']

    itemwithquant = models.ItemWithQuantity.objects.filter(item=itemid, user=self.request.user, visibility=True)

    item = models.Item.objects.get(id=itemid)
    mystore = Store.objects.get(id=store)
    myuser = RegularAccount.objects.get(id=client)

    if itemwithquant:
        for i in itemwithquant:
            i.user = self.request.user
            i.quantity = i.quantity + 1
            i.save()
    else:
        newitemwithquant = models.ItemWithQuantity(user=self.request.user, item=item)
        newitemwithquant.save()

        if additives:
            addadditives = models.ItemWithQuantity.objects.get(item=itemid, user=self.request.user, visibility=True)
            for j in additives:
                addadditives.addedadditives.add(j)
                print(addadditives.addedadditives)
            addadditives.total = addadditives.item.cost * addadditives.quantity
            addadditives.total = addadditives.total + addadditives.totaladditiveprice
            addadditives.save()

    newitemwithquant = models.ItemWithQuantity.objects.filter(item=item, user=self.request.user, visibility=True)
    cart = models.ModelCart.objects.filter(check=store + client, visibility=True)

    if cart:
        for j in cart:
            for i in j.listitem.all():
                for q in newitemwithquant:
                    j.listitem.add(q)
                    j.save()
    else:
        newcart = models.ModelCart(
            clientid=myuser, storeid=mystore, check=store + client
        )
        newcart.save()
        addcart = models.ModelCart.objects.filter(check=store + client, visibility=True)

        for i in addcart:
            for q in newitemwithquant:
                i.listitem.add(q)
                i.save()


def create_order_in_firebase(saved_data, currentuser):
    models.save_action(saved_data.storeId, saved_data, None, saved_data.status, currentuser, saved_data.clientId)
    models.save_score_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.scoregot,
                             saved_data.scorepaid)

    if saved_data.paymentStatus == True and saved_data.paymentType == 2:
        models.save_payment_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.paymentType,
                                   saved_data.totalprice)

    saved_data.clientId.score = saved_data.clientId.score - saved_data.scorepaid
    saved_data.clientId.save()
    data = {
        u'id': saved_data.id, u'clientId': saved_data.clientId.id, u'storeId': saved_data.storeId.id,
        u'paymentType': saved_data.paymentType, u'paymentStatus': saved_data.paymentStatus,
        u'phone': saved_data.clientId.phone,
        u'status': saved_data.status, u'timedelivery': saved_data.timedelivery, u'totalprice': saved_data.totalprice,
        u'totalcount': saved_data.totalcount,
        u'ordertype': saved_data.ordertype, u'declinereason': saved_data.declinereason,
        u'refusereason': saved_data.refusereason, u'deliverycost': saved_data.storeId.deliverycost,
        u'scorepaid': saved_data.scorepaid, u'scoregot': saved_data.scoregot, u'address': saved_data.address,
        u'comment': saved_data.comment, u'date': saved_data.date
    }
    firestore.db.collection(u'stores').document(str(saved_data.storeId.id)).collection(u'orders').document(
        str(saved_data.id)).set(data)

    for i in saved_data.cart.listitem.all():
        images = []
        for j in i.item.images.all():
            image = {
                u'image': j.image
            }
            images.append(j.image)
        item = {
            u'id': i.item.id, u'name': i.item.name, u'cost': i.item.cost, u'images': images, u'total': i.total,
            u'quantity': i.quantity
        }
        firestore.db.collection(u'stores').document(str(saved_data.storeId.id)).collection(u'orders').document(
            str(saved_data.id)).collection(u'items').document(
            str(i.item.id)).set(item)

    saved_data.cart.visibility = False
    for i in saved_data.cart.listitem.all():
        print(i)
        i.visibility = False
        print("After", i.visibility)
        i.save()

    saved_data.cart.save()


def update_status(saved_data, prev_status, currentuser):
    if saved_data.status == 1:
        firestore.db.collection(u'stores').document(str(saved_data.storeId.id)).collection(u'orders').document(
            str(saved_data.id)).update({"status": 1})
        models.save_action(saved_data.storeId, saved_data, None, saved_data.status, saved_data.currentuser, saved_data.clientId)

        if saved_data.paymentStatus==True and saved_data.paymentType==2:
            models.save_payment_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.paymentType,
                               saved_data.totalprice)

    elif saved_data.status == 2:
        models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)

    elif saved_data.status == 3:
        models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)

    elif saved_data.status == 4:
        models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)

    elif saved_data.status == 5:
        if saved_data.iscourier == True:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, 'Курьер', saved_data.clientId)
        else:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)

    elif saved_data.status == 6:
        models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)
        models.save_score_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.scoregot,
                                 saved_data.scorepaid)
        if saved_data.paymentStatus==True and saved_data.paymentType==1:
            models.save_payment_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.paymentType,
                               saved_data.totalprice)

    elif saved_data.status == 7:
        if saved_data.iscourier == True:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, 'Курьер',
                               saved_data.clientId)
        else:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser,
                               saved_data.clientId)

    elif saved_data.status == 8:
        if saved_data.iscourier == True:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, 'Курьер', saved_data.clientId)
        else:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)

        models.save_score_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.scoregot,
                                 saved_data.scorepaid)

        if saved_data.paymentStatus==True and saved_data.paymentType==1:
            models.save_payment_action(saved_data.clientId, saved_data.storeId, saved_data, saved_data.paymentType,
                               saved_data.totalprice)

    elif saved_data.status == 9:
        if saved_data.iscourier == True:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, 'Курьер', saved_data.clientId)
        else:
            models.save_action(saved_data.storeId, saved_data, prev_status, saved_data.status, currentuser, saved_data.clientId)


def paybox_integration(order_id, amount, description):


    print(description)

    def hash_md5(data):
        return hashlib.md5(data.encode()).hexdigest()

    def sort_children_by_name(parent):
        parent[:] = sorted(parent, key=attrgetter("tag"))


    root = ET.Element('request')

    merchant_id = ET.SubElement(root, 'pg_merchant_id')
    merchant_id.text = settings.MERCHANT_ID

    pg_amount = ET.SubElement(root, 'pg_amount')
    pg_amount.text = str(amount)

    pg_order_id = ET.SubElement(root, 'pg_order_id')
    pg_order_id.text = str(order_id)

    pg_description = ET.SubElement(root, 'pg_description')
    pg_description.text = description

    pg_salt = ET.SubElement(root, 'pg_salt')
    pg_salt.text = get_random_string()

    sort_children_by_name(root)

    data = [node.text for node in root.findall("*")]
    data = ['init_payment.php'] + data + [settings.PAY_SECRET_KEY]

    pg_sig = ET.SubElement(root, 'pg_sig')
    pg_sig.text = hash_md5(';'.join(data))
    # print(ET.dump(root))

    payment_url = 'https://api.paybox.money/init_payment.php'
    response = requests.post(payment_url, data={'pg_xml': ET.tostring(root, encoding='utf8', method='xml')})
    response_xml = ET.fromstring(response.content.decode())
    print(response_xml)
    pg_redirect_url = (response_xml.find('pg_redirect_url').text)
    print(pg_redirect_url)
    return pg_redirect_url

#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