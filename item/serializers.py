from django.contrib.auth import get_user_model
from rest_framework import serializers
from item import models
from rest_framework.response import Response
from user.serializers import StoreSerializer, RegularAccountSerializer


class MyStore(serializers.ModelSerializer):
    """To show store with less data"""

    class Meta:
        model = models.Store
        fields = ('id', 'name','login', 'phone', 'email', 'avatar',
                  'storeaddress', 'worktime', 'deliverycost', 'avgcheck',
                 )
        read_only_field = ('id',)


class ItemCategorySerializer(serializers.ModelSerializer):
    """Serializer for item category"""
    class Meta:
        model = models.ItemCategory
        fields = ('id', 'name', 'supplier')
        read_only_fields = ('id',)


class ItemAdditiveSerializer(serializers.ModelSerializer):
    """Serializer for additive(Добавки)"""
    class Meta:
        model = models.ItemAdditive
        fields = (
            'id', 'name', 'cost'
        )
        read_only_fields = ('id',)


class ItemImagesSerializer(serializers.ModelSerializer):
    """Serializer for item Images"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.ItemImages
        fields = ('id', 'image',)


class TakeTogetherSerializer(serializers.ModelSerializer):
    """Serializer for taketogether"""
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.Item
        fields = (
            'id', 'name', 'description', 'itemcategory',
            'currency', 'cost', 'sostav', 'gram', 'ccal', 'images',
            'protein', 'fats', 'carbo', 'costsale', 'supplier'
        )
        read_only_fields = ('id',)


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for item serializer"""
    additive = ItemAdditiveSerializer(many=True, required=False, allow_null=True)
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)

    taketogether = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Item.objects.all()
    )

    class Meta:
        model = models.Item
        fields = (
            'id', 'additive', 'name', 'description', 'itemcategory',
            'currency', 'cost', 'sostav', 'gram', 'ccal', 'images',
            'protein', 'fats', 'carbo', 'costsale', 'taketogether',
            'supplier'
        )
        read_only_fields = ('id', 'isfavourite')

    def create(self, validated_data):

        a= validated_data.get('taketogether', None)
        additive = validated_data.pop("additive", None)
        taketogether = validated_data.pop("taketogether", None)

        images = validated_data.pop("images", None)
        item = models.Item.objects.create(**validated_data)

        for i in a:
            item.taketogether.add(i)

        if additive:
            for i in additive:
                models.ItemAdditive.objects.create(item=item, **i)

        if images:
            for i in images:
                models.ItemImages.objects.create(item=item, **i)

        return item


    def update(self, instance, validated_data):

        taketogether = validated_data.pop("taketogether", None)

        if taketogether:
            for j in instance.taketogether.all():
                instance.taketogether.remove(j)

            for i in taketogether:
                instance.taketogether.add(i)
                instance.save()


        additive = validated_data.pop('additive', None)
        item = (instance.additive).all()
        item = list(item)

        images = validated_data.pop('images', None)

        itemimage = (instance.images).all()
        itemimage = list(itemimage)
        saveimage = []

        if images:
            print("I am image", images)
            for i in images:
                print(i)
                if i['image']:
                    saveimage.append(i['image'])

            for j in instance.images.all():
                if j:
                    if str(j) in saveimage:
                        pass
                    else:
                        j.delete()
        else:
            instance.images.all().delete()

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.itemcategory = validated_data.get('itemcategory', instance.itemcategory)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.sostav = validated_data.get('sostav', instance.sostav)
        instance.gram = validated_data.get('gram', instance.gram)
        instance.ccal = validated_data.get('ccal', instance.ccal)
        instance.protein = validated_data.get('protein', instance.protein)
        instance.fats = validated_data.get('fats', instance.fats)
        instance.carbo = validated_data.get('carbo', instance.carbo)
        instance.costsale = validated_data.get('costsale', instance.costsale)
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.save()

        keep_additive = []
        if additive:
            for a in additive:
                if "id" in a.keys():
                    if models.ItemAdditive.objects.filter(id=a["id"]).exists():
                        updateitem = models.ItemAdditive.objects.get(id=a["id"])
                        updateitem.name = a.get('name', updateitem.name)
                        updateitem.cost = a.get('cost', updateitem.cost)
                        updateitem.select = a.get('select', updateitem.select)
                        keep_additive.append(updateitem.id)
                    else:
                        continue
                else:
                    c = models.ItemAdditive.objects.create(**a, item=instance)
                    keep_additive.append(c.id)

            for a in instance.additive:
                if a.id not in keep_additive:
                    a.delete()

        if images:
            for a in images:
                if itemimage:
                    i = itemimage.pop(0)
                    i.id = a.get('id', i.id)
                    i.image = a.get('image', i.image)
                    i.save()
                else:
                    c = models.ItemImages.objects.create(item=instance, **a)
                    c.save()
                    itemimage.append(c.id)

        return instance


class UpdateTakeTogetherSerializer(serializers.ModelSerializer):
    """Update take together"""
    taketogether = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Item.objects.all()
    )

    class Meta:
        model = models.Item
        fields = (
            'id', 'name', 'taketogether'
        )
        read_only_fields = ('id',)


class UpdateTakeTogetherDetailSerializer(UpdateTakeTogetherSerializer):
    """Serilizer for taketogether detil object"""
    taketogether = UpdateTakeTogetherSerializer(many=True)


class GetItemSerializer(serializers.ModelSerializer):
    """Serializer for item serializer"""
    additive = ItemAdditiveSerializer(many=True, required=False, allow_null=True)
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)
    isfavourite = serializers.BooleanField()
    supplier = MyStore()

    class Meta:
        model = models.Item
        fields = (
            'id', 'additive', 'name', 'description', 'itemcategory',
            'currency', 'cost', 'isfavourite', 'sostav', 'gram', 'ccal', 'images',
            'protein', 'fats', 'carbo', 'costsale', 'taketogether', 'salecost',
            'supplier'
        )
        read_only_fields = ('id',)
        depth=1


class ItemShareLink(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Item
        fields = ('url',)

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_url())



class GetCertainItemDataSerializer(serializers.ModelSerializer):
    """Serializer for item serializer"""
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.Item
        fields = (
            'id', 'name', 'images'
        )
        read_only_fields = ('id',)


class RelateItemSerializer(serializers.ModelSerializer):
    """Serializer for item serializer"""
    additive = ItemAdditiveSerializer(many=True, required=False, allow_null=True)
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)
    isfavourite = serializers.BooleanField(default=True)
    supplier = MyStore()

    class Meta:
        model = models.Item
        fields = (
            'id', 'additive', 'name', 'description', 'itemcategory',
            'currency', 'cost', 'isfavourite', 'sostav', 'gram', 'ccal', 'images',
            'protein', 'fats', 'carbo', 'costsale', 'taketogether',
            'supplier'
        )
        read_only_fields = ('id',)
        depth=1


class UserFavouriteItemSerializer(serializers.ModelSerializer):
    """Add store to favourites"""
    class Meta:
        model = models.UserFavouriteItems
        fields = (
            'id', 'item'
        )
        read_only_fields = ('id',)


class GetUserFavouriteItemSerializer(serializers.ModelSerializer):
    """Add store to favourites"""
    item = RelateItemSerializer()
    class Meta:
        model = models.UserFavouriteItems
        fields = (
            'item',
        )


class ModelPostCartSerializer(serializers.Serializer):
    """Create new cart"""
    itemid = serializers.IntegerField()
    client = serializers.IntegerField()
    store = serializers.IntegerField()
    additives = serializers.ListField(required=False, allow_null=True)

    def save(self):
        itemid = self.validated_data['itemid']
        client = self.validated_data['client']
        store = self.validated_data['store']
        additives = self.validated_data['additives']


class RelateItemToCartSerializer(serializers.ModelSerializer):
    """Serializer for item serializer"""
    images = ItemImagesSerializer(many=True, required=False, allow_null=True)
    supplier = MyStore()

    class Meta:
        model = models.Item
        fields = (
            'id', 'name', 'description', 'itemcategory',
            'currency', 'cost', 'sostav', 'gram', 'ccal', 'images',
            'protein', 'fats', 'carbo', 'costsale',
            'supplier'
        )
        read_only_fields = ('id',)
        depth=1


class ListItemSerializer(serializers.ModelSerializer):
    item = RelateItemToCartSerializer()

    class Meta:
        model = models.ItemWithQuantity
        fields = ('id', 'item', 'addedadditives', 'total', 'quantity', 'totaladditiveprice')
        read_only_fields = ('id',)
        depth=1


class DeleteCartSerializer(serializers.Serializer):
    """Delete cart"""
    client = serializers.IntegerField()

    def save(self):
        client = self.validated_data['client']


class ModelCartSerializer(serializers.ModelSerializer):
    """Get cart(busket)"""
    listitem = ListItemSerializer(many=True)
    clientid = RegularAccountSerializer()
    storeid = MyStore()

    class Meta:
        model = models.ModelCart
        fields = ('id', 'listitem', 'clientid', 'storeid', 'totalprice')
        read_only_fields = ('id',)


class RemoveItemNewSerializer(serializers.Serializer):
    """Remove item from cart"""
    item = serializers.IntegerField()
    cart = serializers.IntegerField()

    def save(self):
        item = self.validated_data['item']
        cart = self.validated_data['cart']


class OrderReportSerializer(serializers.ModelSerializer):
    """Order action"""
    total_cost = serializers.IntegerField()

    class Meta:
        model = models.ModelOrder
        fields = (
            'total_cost', 'reporttotal'
        )


class ClientOrderSerializer(serializers.ModelSerializer):
    """Serializer for client order"""
    class Meta:
        model = models.ModelOrder
        fields = (
            'id', 'clientId', 'storeId', 'paymentType', 'paymentStatus', 'ordertype',
            'timedelivery', 'scorepaid', 'scoregot', 'address', 'declinereason', 'status',
            'quantityappliances', 'scancode', 'comment', 'date', 'cart'
        )
        read_only_fields = ('id',)


class RelateCartSerializer(serializers.ModelSerializer):
    """Get cart(busket)"""
    listitem = ListItemSerializer(many=True)

    class Meta:
        model = models.ModelCart
        fields = ('listitem',)


class GetClientOrderSerializer(serializers.ModelSerializer):
    """Serializer for client order"""
    is_rated = serializers.BooleanField()
    storeId = MyStore()
    clientId = RegularAccountSerializer()
    cart = RelateCartSerializer()

    class Meta:
        model = models.ModelOrder
        fields = (
            'id', 'clientId', 'storeId', 'paymentType', 'paymentStatus', 'status',
            'timedelivery', 'scorepaid', 'scoregot', 'address', 'ordertype', 'totalprice', 'totalcount', 'is_rated',
            'quantityappliances', 'scancode', 'comment', 'date', 'cart', 'declinereason', 'refusereason'
        )
        read_only_fields = ('id',)


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for client address"""

    class Meta:
        model = models.Address
        fields = (
            'id', 'name', 'city', 'street', 'numhouse', 'entrance', 'floor',
            'phone', 'location', 'longitude', 'latitude'
        )
        read_only_fields = ('id',)


class MyOrderSerializer(serializers.ModelSerializer):
    """Serializer for client order"""
    cart = RelateCartSerializer()

    class Meta:
        model = models.ModelOrder
        fields = (
            'id', 'paymentType', 'paymentStatus', 'status', 'ordertype',
            'status', 'totalprice', 'totalcount', 'timedelivery', 'scorepaid', 'scoregot',
            'date', 'cart'
        )
        read_only_fields = ('id',)


class OrderReviewSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""

    class Meta:
        model = models.OrderReview
        fields = ('id', 'star', 'store', 'user', 'text', 'date', 'order')
        read_only_fields = ('id',)


class GetOrderReviewSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""
    user = RegularAccountSerializer()
    store = MyStore()
    order = MyOrderSerializer()

    class Meta:
        model = models.OrderReview
        fields = ('id', 'star', 'store', 'user', 'text', 'date', 'order')
        read_only_fields = ('id',)


class OrderActionSerializer(serializers.ModelSerializer):
    """Order action"""
    class Meta:
        model = models.SaveOrderActions
        fields = (
            'id', 'store', 'order', 'prev_status', 'status', 'changedby', 'date', 'user'
        )
        read_only_fields = ('id',)


class ScoreActionsSerializer(serializers.ModelSerializer):
    """Order action"""
    class Meta:
        model = models.ScoreActions
        fields = (
            'id', 'user', 'store', 'order', 'scoregot', 'scorepaid', 'date'
        )
        read_only_fields = ('id',)


class PaymentActionSerializer(serializers.ModelSerializer):
    """Order action"""
    class Meta:
        model = models.SavePaymentAction
        fields = (
            'id', 'user', 'store', 'order', 'paymentType', 'totalprice', 'date'
        )
        read_only_fields = ('id',)


class ReportSerializer(serializers.ModelSerializer):
    """Report serializer"""

    class Meta:
        model = models.Report
        fields = (
            'total',
        )
        read_only_fields = ('total',)


class DeleteSeveralItemsSerializer(serializers.Serializer):
    """Create new cart"""
    items = serializers.ListField(required=False, allow_null=True)

    def save(self):
        items = self.validated_data['items']
