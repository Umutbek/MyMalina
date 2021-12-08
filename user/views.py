from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework import permissions, status, generics, authentication
from rest_framework.decorators import api_view, permission_classes, action

from .permissions import IsStoreOrReadOnly, IsRegular

from user import models, serializers, filter
from item.serializers import AddressSerializer
from item.models import Address
from django.shortcuts import get_object_or_404

from django.db.models import Sum, Count, F, Q


class StoreViewSet(viewsets.ModelViewSet):
    """Manage Store"""
    permission_classes = (permissions.AllowAny,)
    queryset = models.Store.objects.all()
    serializer_class = serializers.StoreSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.StoreFilter
    search_fields = ('name', 'description', 'slogan')

    def get_queryset(self):
        """Check is store selected as favourite or not"""
        store = self.queryset.all().annotate(
            isfavouritestore=Count("fav_store",
                                     filter=Q(fav_store__client=self.request.user.id))
        ).annotate(
            rating=Sum(F('rate_store_order__star')) / Count(F('rate_store_order'))
        )
        return store


    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetStoreSerializer

        return serializers.StoreSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class StoreShareLinkView(generics.RetrieveAPIView):
    """Link for item share"""
    serializer_class = serializers.StoreShareLink
    queryset = models.Store.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    """Manage Regular account"""
    permission_classes = (permissions.AllowAny,)
    queryset = models.RegularAccount.objects.all()
    serializer_class = serializers.RegularAccountSerializer

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name', 'login')


class RatingViewSet(viewsets.ModelViewSet):
    """Rate Store"""
    serializer_class = serializers.CreateRatingSerializer
    permission_classes = (IsRegular,)
    queryset = models.Rating.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LoginAPI(TokenObtainPairView):
    """Get token"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer


class StoreLoginAPI(TokenObtainPairView):
    """Get token"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginStoreSerializer


class RefreshTokenView(TokenRefreshView):
    """Refresh token, if access token's time is up"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.RefreshTokenSerializer


class UserFavouriteStoreViewSet(viewsets.ModelViewSet):
    """User selects favourite stores"""

    permission_classes = (IsRegular,)
    queryset = models.UserFavouriteStore.objects.all()
    lookup_field = 'store'

    def get_queryset(self):
        """Retrieve the favourite stores for the authenticated user only"""
        return self.queryset.filter(client=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(client=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetUserFavouriteStoreSerializer

        return serializers.UserFavouriteStoreSerializer


class GetMeView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user


class GetQrCodeView(APIView):
    """Create new user in system"""
    serializer_class = serializers.GetQrCodeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """Return a list of category details"""
        code = models.RegularAccount.objects.filter(id=self.request.user.id).first()
        print("Code", code)
        serializer = serializers.GetQrCodeSerializer(code)
        return Response(serializer.data)


class GetPointsView(APIView):
    """Create new user in system"""
    serializer_class = serializers.GetPointsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """Return a list of category details"""
        point = models.RegularAccount.objects.filter(id=self.request.user.id).first()
        serializer = serializers.GetPointsSerializer(point)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """Manage global category"""
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all().order_by('-available', 'name')
    pagination_class = None


class SubcategoryViewSet(viewsets.ModelViewSet):
    """Manage store categories"""

    serializer_class = serializers.SubCategorySerializer
    queryset = models.Subcategory.objects.all()
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.SubcategoryFilter


class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = serializers.PasswordChangeSerializer
    model = models.Store
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"detail": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code':200,
                'detail': 'Password updated successfully',
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDeliveryCostView(generics.RetrieveUpdateAPIView):

    serializer_class = serializers.StoreDeliveryCostSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        object = models.Store.objects.get(pk=kwargs['pk'])
        serializer = serializers.StoreDeliveryCostSerializer(object)
        return Response(serializer.data)


class WithDrawScoreViewSet(viewsets.ModelViewSet):
    """WithDraw score of user's """
    serializer_class = serializers.WithdrawScoreSerializer
    queryset = models.WithDrawScore.objects.all()
    pagination_class = None

    def get_queryset(self):
        """Retrieve the favourite stores for the authenticated user only"""
        return self.queryset.filter(client=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """Add new address for user"""
    permission_classes = (IsRegular,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    pagination_class = None

    def get_queryset(self):
        """Retrieve the address for the authenticated user only"""
        return self.queryset.filter(client=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(client=self.request.user)


class AppPromptViewSet(viewsets.ModelViewSet):
    """Добавление рейтинга фильму"""
    serializer_class = serializers.AppPromptSerializer
    queryset = models.AppPrompt.objects.all()
    pagination_class = None
