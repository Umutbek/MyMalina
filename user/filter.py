from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django_filters import rest_framework as filters
from item.models import Item, ItemCategory
from user.models import Store


class StoreFilter(FilterSet):
    """Filter for an item"""
    subcategory = filters.CharFilter('subcategory')

    class Meta:
        models = Store
        fields = ('subcategory',)


class SubcategoryFilter(FilterSet):
    """Filter for an item"""
    category = filters.CharFilter('category')

    class Meta:
        models = Store
        fields = ('category',)
