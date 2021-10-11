from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django_filters import rest_framework as filters
from item.models import Item, ItemCategory, ModelOrder, SaveOrderActions


class ItemFilter(FilterSet):
    """Filter for an item"""
    supplier = filters.CharFilter('supplier')
    itemcategory = filters.CharFilter('itemcategory')

    class Meta:
        models = Item
        fields = ('supplier', 'itemcategory')


class ItemCategoryFilter(FilterSet):
    """Filter for an item"""
    supplier = filters.CharFilter('supplier')

    class Meta:
        models = ItemCategory
        fields = ('supplier',)


class OrderFilter(FilterSet):
    """Filter for an item"""
    clientId = filters.CharFilter('clientId')
    storeId = filters.CharFilter('storeId')
    start_date = filters.DateFilter(field_name="date", lookup_expr='gte')
    end_date = filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        models = ModelOrder
        fields = ('clientId', 'storeId', 'start_date', 'end_date')


class ActionFilter(FilterSet):
    """Filter for an item"""
    user = filters.CharFilter('user')
    store = filters.CharFilter('store')
    order = filters.CharFilter('order')

    class Meta:
        models = SaveOrderActions
        fields = ('user', 'store', 'order')