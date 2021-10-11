from user.models import RegularAccount, Store
from item import models, firestore


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

#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