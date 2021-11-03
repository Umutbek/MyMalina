from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
import jwt
from django.conf import settings
from django.contrib.auth.models import update_last_login
from user import models, utils
from item import firestore

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name','login', 'phone', 'email', 'avatar', 'type')
        read_only_fields = ('id', 'code', 'score')


    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        return self.Meta.model.objects.create_user(**validated_data)


class RegularAccountSerializer(UserSerializer):

    class Meta:
        model = models.RegularAccount
        fields = ('id', 'name', 'surname', 'login', 'phone', 'email', 'avatar', 'type',
                  'datebirth', 'gender', 'code', 'score', 'device_id'
                  )


class GetQrCodeSerializer(UserSerializer):

    class Meta:
        model = models.RegularAccount
        fields = ('code', 'score')


class GetPointsSerializer(UserSerializer):

    class Meta:
        model = models.RegularAccount
        fields = ('score',)


class StoreAddress(serializers.Serializer):
    """Store address serializer"""
    name = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    longitude = serializers.CharField(required=False, allow_null=True)
    latitude = serializers.CharField(required=False, allow_null=True)


class StoreSerializer(UserSerializer):
    storeaddress = StoreAddress()

    class Meta:
        model = models.Store
        fields = ('id', 'name','login', 'phone', 'email', 'avatar', 'type', 'password',
                  'percentage', 'storeaddress', 'worktime', 'telegram', 'deliverycost', 'avgcheck',
                  'instagram', 'whatsapp', 'slogan', 'description', 'category', 'subcategory', 'is_staff')

        read_only_field = ('id',)
        extra_kwargs = {'password':{'write_only':True},}


class GetStoreSerializer(UserSerializer):

    isfavouritestore = serializers.BooleanField()
    is_rated = serializers.BooleanField()
    rating = serializers.IntegerField()

    class Meta:
        model = models.Store
        fields = ('id', 'name','login', 'phone', 'email', 'avatar', 'type', 'password',
                  'percentage', 'storeaddress', 'worktime', 'telegram', 'deliverycost', 'avgcheck',
                  'instagram', 'whatsapp', 'slogan', 'description', 'is_rated', 'rating',
                  'category', 'isfavouritestore', 'subcategory', 'is_staff')

        read_only_field = ('id',)
        extra_kwargs = {'password':{'write_only':True},}


class StoreShareLink(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Store
        fields = ('url',)

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_url())


class StoreDeliveryCostSerializer(UserSerializer):

    class Meta:
        model = models.Store
        fields = ('id', 'name','login', 'deliverycost')

        read_only_field = ('id',)


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_id = jwt.decode(data['access'], settings.SECRET_KEY, algorithms='HS256').get('user_id', None)
        user = models.User.objects.get(id=user_id)
        if user:
            data['user'] = UserSerializer(user).data

        return data


class LoginSerializer(TokenObtainPairSerializer, serializers.ModelSerializer):

    default_error_messages = {
        'no_active_account': 'Wrong login or password',
        'no_user': 'User does not exist'
    }

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        key = attrs.get('key')

        try:
            malinauser = models.User.objects.get(login=login)
        except models.User.DoesNotExist:
            user = models.RegularAccount(login=login, password=password, type=1)
            user.set_password(attrs['password'])
            user.save()

        fkey = firestore.db.collection(u'key').document(u'2UHxFdcx5JQHgS5oUnnN').get()
        fkey = fkey.to_dict()

        if key != fkey['key']:
            raise AuthenticationFailed("Wrong key")
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        data['user'] = UserSerializer(self.user).data
        update_last_login(None, self.user)
        return data

    key = serializers.CharField()
    class Meta:
        model = User
        fields = ('login', 'password', 'key')


class LoginStoreSerializer(TokenObtainPairSerializer, serializers.ModelSerializer):

    default_error_messages = {
        'no_active_account': 'Wrong login or password',
        'no_user': 'User does not exist'
    }

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        try:
            malinauser = models.User.objects.get(login=login)
        except models.User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_user']
            )
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        data['user'] = UserSerializer(self.user).data
        update_last_login(None, self.user)
        return data

    class Meta:
        model = User
        fields = ('login', 'password')


class RelateStoreSerializer(UserSerializer):

    isfavouritestore = serializers.BooleanField(default=True)

    class Meta:
        model = models.Store
        fields = ('id', 'name', 'phone', 'avatar', 'email', 'storeaddress', 'worktime', 'telegram', 'deliverycost', 'avgcheck',
                  'instagram', 'whatsapp', 'slogan', 'description', 'category', 'isfavouritestore', 'subcategory')
        read_only_field = ('id',)
        depth=1


class UserFavouriteStoreSerializer(serializers.ModelSerializer):
    """Add store to favourites"""
    class Meta:
        model = models.UserFavouriteStore
        fields = (
            'id', 'store'
        )
        read_only_fields = ('id',)


class GetUserFavouriteStoreSerializer(serializers.ModelSerializer):
    """Add store to favourites"""
    store = RelateStoreSerializer()
    class Meta:
        model = models.UserFavouriteStore
        fields = (
            'store',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for global category: meals, sport etc..."""
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'icon', 'available')
        read_only_fields = ('id',)


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for store category"""
    class Meta:
        model = models.Subcategory
        fields = ('id', 'name', 'icon', 'category')
        read_only_fields = ('id',)


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    model = models.Store
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class WithdrawScoreSerializer(serializers.ModelSerializer):
    """Serializer for withdraw scores"""
    class Meta:
        model = models.WithDrawScore
        fields = ('id', 'client', 'score', 'date')
        read_only_fields = ('id',)

    def create(self, validated_data):
        withdraw = models.WithDrawScore.objects.create(**validated_data)
        withdraw.client.score = withdraw.client.score - withdraw.score

        withdraw.client.save()
        return withdraw


class CreateRatingSerializer(serializers.ModelSerializer):
    """Add rating"""
    class Meta:
        model = models.Rating
        fields = ("star", "store", "text", 'date')

    def create(self, validated_data):

        rating, _ = models.Rating.objects.update_or_create(
            user=validated_data.get('user', None),
            store=validated_data.get('store', None),
            defaults={'star': (validated_data.get("star")), 'text':(validated_data.get("text"))}
        )
        return rating


class AppPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPrompt
        fields = ('id', 'type', 'text')
        read_only_fields = ('id',)