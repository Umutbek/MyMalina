from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import permissions, status, generics
from rest_framework.decorators import api_view, permission_classes, action

from item import models, serializers, firestore
from user.models import RegularAccount, Store

from django.shortcuts import get_object_or_404

from user.permissions import IsStoreOrReadOnly, IsRegular
from item import filter, functions
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Sum, Count, F, Q
from django.http import Http404
from rest_framework_xml.parsers import XMLParser



class ItemCategoryViewSet(viewsets.ModelViewSet):
    """Manage item category"""
    serializer_class = serializers.ItemCategorySerializer
    queryset = models.ItemCategory.objects.all()
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.ItemCategoryFilter


class ItemViewSet(viewsets.ModelViewSet):
    """Manage item"""

    queryset = models.Item.objects.all()

    def get_queryset(self):
        """Retrieve the favourite stores for the authenticated user only"""

        item = self.queryset.all().annotate(
            isfavourite=Count("fav_items",
                                     filter=Q(fav_items__user=self.request.user.id)))
        return item

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetItemSerializer

        return serializers.ItemSerializer

    def get_serializer_context(self):
        return {'request':self.request}


    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.ItemFilter
    search_fields = ('name', 'description', 'itemcategory__name')


class ItemShareLinkView(generics.RetrieveAPIView):
    """Link for item share"""
    serializer_class = serializers.ItemShareLink
    queryset = models.Item.objects.all()


class GetItemViewSet(viewsets.ModelViewSet):
    """Manage item with certain data"""

    queryset = models.Item.objects.all()
    serializer_class = serializers.GetCertainItemDataSerializer
    pagination_class = None

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.ItemFilter
    search_fields = ('name',)


class UserFavouriteItemViewSet(viewsets.ModelViewSet):
    """User selects favourite item"""

    permission_classes = (IsRegular,)

    queryset = models.UserFavouriteItems.objects.all()
    lookup_field = 'item'

    def get_queryset(self):
        """Retrieve the favourite stores for the authenticated user only"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetUserFavouriteItemSerializer

        return serializers.UserFavouriteItemSerializer



class ItemAdditiveViewSet(viewsets.ModelViewSet):
    """Manage item additives"""
    serializer_class = serializers.ItemAdditiveSerializer
    queryset = models.ItemAdditive.objects.all()
    pagination_class = None


class CartViewSet(viewsets.ModelViewSet):
    """Manage Cart(Busket)"""
    permission_classes = (IsRegular,)

    queryset = models.ModelCart.objects.all()
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(clientid=self.request.user, visibility=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ModelPostCartSerializer
        return serializers.ModelCartSerializer


    def create(self, request, *args, **kwargs):
        serializer = serializers.ModelPostCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        functions.create_cart(self, serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        print("Cart", cart)
        for i in cart.listitem.all():
            print("I", i)
            i.delete()
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveItem(APIView):
    serializer_class = serializers.RemoveItemNewSerializer

    def post(self, request):
        serializer = serializers.RemoveItemNewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.validated_data['cart']
        item = serializer.validated_data['item']
        usercart = models.ModelCart.objects.filter(id=cart, visibility=True).first()
        if usercart:
            for i in usercart.listitem.all():

                if item == i.item.id and i.quantity>1:
                    i.quantity = i.quantity - 1
                    i.save()
                elif item == i.item.id and i.quantity == 1:
                    if usercart.listitem.count() == 1:
                        usercart.delete()
                        break
                    i.delete()

            return Response({"detail": "Removed successfully"})
        else:
            return Response({"detail": "No cart with this id"}, status=404)


class RemoveCartItem(APIView):
    serializer_class = serializers.RemoveItemNewSerializer

    def post(self, request):
        serializer = serializers.RemoveItemNewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.validated_data['cart']
        item = serializer.validated_data['item']
        usercart = models.ModelCart.objects.filter(id=cart, visibility=True).first()
        if usercart:
            for i in usercart.listitem.all():

                if item == i.item.id:
                    if usercart.listitem.count() == 1:
                        usercart.delete()
                        i.delete()
                        break
                    i.item.delete()

            return Response({"detail": "Removed successfully"})
        else:
            return Response({"detail": "No cart with this id"}, status=404)


class DeleteCartsView(APIView):
    serializer_class = serializers.DeleteCartSerializer

    def post(self, request):
        serializer = serializers.DeleteCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.validated_data['client']
        usercart = models.ModelCart.objects.filter(clientid=client, visibility=True)
        itemwithcount = models.ItemWithQuantity.objects.filter(user=client, visibility=True)

        if usercart and itemwithcount:
            for i in usercart:
                i.delete()
            for i in itemwithcount:
                i.delete()
            return Response({"detail": "Cart deleted successfully"})
        else:
            return Response({"detail": "User cart doesn't exist"}, status=404)


class ClientOrderViewSet(viewsets.ModelViewSet):
    """Manage clientorder"""
    serializer_class = serializers.ClientOrderSerializer
    queryset = models.ModelOrder.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = filter.OrderFilter

    def get_queryset(self):
        order = self.queryset.all().order_by('-id').annotate(
            is_rated=Count("reviews",filter=Q(reviews__user=self.request.user.id))
        )
        return order

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetClientOrderSerializer
        return serializers.ClientOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.ClientOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_data = serializer.save()

        saved_data.orderdelivery_cost = saved_data.storeId.deliverycost

        if saved_data.scorepaid > saved_data.clientId.score:
            saved_data.delete()
            return Response({"detail": "Not enough score"})

        functions.create_order_in_firebase(saved_data, self.request.user.name)
        if saved_data.paymentType == 2:
            if saved_data.comment:
                paybox_response = functions.paybox_integration(saved_data.id, saved_data.totalprice,
                                             saved_data.comment)
            else:
                paybox_response = functions.paybox_integration(saved_data.id, saved_data.totalprice,
                                             'No comment')
            return Response({
                'redirect_url': paybox_response['pg_redirect_url'],
                'order_id': paybox_response['pg_order_id']
            })

        saved_data.save()
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """Add new address for user"""
    serializer_class = serializers.AddressSerializer
    queryset = models.Address.objects.all()
    pagination_class = None

    def get_queryset(self):
        """Retrieve the address for the authenticated user only"""
        return self.queryset.filter(client=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(client=self.request.user)


class StatusUpdateView(generics.RetrieveUpdateAPIView):
    """Create new user in system"""
    permission_classes = (AllowAny,)
    serializer_class = serializers.ClientOrderSerializer
    queryset = models.ModelOrder.objects.all()

    def partial_update(self, request, *args, **kwargs):
        self.object = self.get_object()
        prev_status = self.object.status
        serializer = self.get_serializer(self.object, data=request.data, partial=True)
        if serializer.is_valid():
            saved_data = serializer.save()
            functions.update_status(self.object, prev_status, self.request.user.name)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetClientOrderView(generics.ListAPIView):
    """Create new user in system"""
    serializer_class = serializers.GetClientOrderSerializer
    queryset = models.ModelOrder.objects.all().order_by('-id')
    pagination_class = None


class OrderRateViewSet(viewsets.ModelViewSet):
    """Rate order"""
    serializer_class = serializers.OrderReviewSerializer
    queryset = models.OrderReview.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetOrderReviewSerializer
        return serializers.OrderReviewSerializer


class ItemWithQuantityViewSet(viewsets.ModelViewSet):
    """Rate order"""
    permission_classes = (AllowAny,)
    serializer_class = serializers.ListItemSerializer
    queryset = models.ItemWithQuantity.objects.all()


class OrderReportView(generics.ListAPIView):
    """List of order actions"""
    serializer_class = serializers.ClientOrderSerializer
    queryset = models.ModelOrder.objects.all()
    pagination_class = None

    def list(self, request, *args, **kwargs):

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        storeId = request.query_params.get('storeId')
        report = models.ModelOrder.objects.all()
        total = sum(i.cart.totalprice for i in report)

        if date_from is not None:
            report = models.ModelOrder.objects.filter(date__date__gte=date_from)
            total = sum(i.cart.totalprice for i in report)

        if date_to is not None:
            report = models.ModelOrder.objects.filter(date__date__lte=date_to)
            total = sum(i.cart.totalprice for i in report)

        if storeId is not None:
            report = models.ModelOrder.objects.filter(storeId=storeId)
            total = sum(i.cart.totalprice for i in report)

        totalcost = models.Report.objects.all().first()
        if totalcost:
            totalcost.total = total
            totalcost.save()
        else:
            totalcost = models.Report(total=total)
            totalcost.save()

        serializer = serializers.ClientOrderSerializer(report, many=True)
        reportserializer = serializers.ReportSerializer(totalcost)
        return Response(reportserializer.data)


class OrderActionView(generics.ListAPIView):
    """List of order actions"""
    serializer_class = serializers.OrderActionSerializer
    queryset = models.SaveOrderActions.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):

        order = request.query_params.get('order')
        action = models.SaveOrderActions.objects.all()

        if order is not None:
            action = models.SaveOrderActions.objects.filter(order=order)
            serializer = self.get_serializer(action, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(action)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(action, many=True)
        return Response(serializer.data)


class PaymentActionView(generics.ListAPIView):
    """List of order actions"""
    serializer_class = serializers.PaymentActionSerializer
    queryset = models.SavePaymentAction.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):

        order = request.query_params.get('order')
        action = models.SavePaymentAction.objects.all()

        if order is not None:
            action = models.SavePaymentAction.objects.filter(order=order)
            serializer = self.get_serializer(action, many=True)
            return Response(serializer.data)


        page = self.paginate_queryset(action)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(action, many=True)
        return Response(serializer.data)


class ScoreActionView(generics.ListAPIView):
    """List of order actions"""
    serializer_class = serializers.ScoreActionsSerializer
    queryset = models.ScoreActions.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):

        order = request.query_params.get('order')
        action = models.ScoreActions.objects.all()

        if order is not None:
            action = models.ScoreActions.objects.filter(order=order)
            serializer = self.get_serializer(action, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(action)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(action, many=True)
        return Response(serializer.data)


class AddTakeTogetherView(generics.RetrieveUpdateAPIView):
    """Update take together"""
    permission_classes = (AllowAny,)
    queryset = models.Item.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.UpdateTakeTogetherDetailSerializer
        return serializers.UpdateTakeTogetherSerializer


class DeleteSeveralItemsView(APIView):
    """Rate order"""
    serializer_class = serializers.DeleteSeveralItemsSerializer

    def post(self, request):
        """Write review"""
        serializer = serializers.DeleteSeveralItemsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            items = serializer.validated_data['items']
            for i in items:
                item = models.Item.objects.filter(id=i).first()
                if item:
                    item.delete()
                else:
                    continue

            return Response({"detail": "Deleted successfully"})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class PaymentResult(APIView):
    """Paybox result"""
    serializer_class = serializers.PaymentResultSerializer
    permission_classes = (AllowAny,)
    parser_classes = [XMLParser]


    def post(self, request):

        serializer = serializers.PaymentResultSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            if int(saved_data.pg_result)==1:
                saved_data.status = 'Success'
                saved_data.save()
            else:
                saved_data.status = 'Failed'
                saved_data.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class PaymentResultDetail(generics.RetrieveAPIView):
    """Check order payment status"""
    serializer_class = serializers.PaymentResultSerializer
    queryset = models.PaymentItem.objects.all()
    lookup_field = 'pg_order_id'


class StoreItemView(generics.ListAPIView):
    """API view to search items and it's store by keyword"""
    serializer_class = serializers.GetItemSerializer
    queryset = models.Item.objects.all().order_by('-id')
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'description', 'itemcategory__name')

    def get_queryset(self):
        """Retrieve the favourite stores for the authenticated user only"""

        item = self.queryset.all().annotate(
            isfavourite=Count("fav_items",
                                     filter=Q(fav_items__user=self.request.user.id)))
        return item

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        search = self.request.query_params.get('search')

        parentlist, childlist, checklist = ([] for i in range(3))
        parentdict, childdict, listdict = ({} for i in range(3))

        if search:
            for l in queryset:
                search = search.lower()
                if search in l.name.lower():
                    listdict['lst_%i' % l.supplier.id] = []

            for i in queryset:
                search = search.lower()
                if search in i.name.lower():
                    childdict = {
                        "id": i.id,
                        "name": i.name,
                        "cost": i.cost,
                        "salecost":i.salecost,
                        "images": str(i.images.all().first())
                    }
                    for j in parentlist:
                        if j['supplier'] in checklist:
                            pass
                        else:
                            checklist.append(j['supplier'])

                    if i.supplier.name in checklist:
                        listdict['lst_%i' % i.supplier.id].append(childdict)

                    else:
                        listdict['lst_%i' % i.supplier.id].append(childdict)
                        parentdict = {
                            "id": i.supplier.id,
                            "supplier": i.supplier.name,
                            "avatar": i.supplier.avatar,
                            "items": listdict['lst_%i' % i.supplier.id]
                        }
                        parentlist.append(parentdict)

            return Response(parentlist)
        else:
            return Response({"detail": "no searching"})



