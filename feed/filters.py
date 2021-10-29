from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet
from django_filters import rest_framework as filters
from feed.models import Article


class ArticleFilter(FilterSet):
    """Article filter by type(sales or news)"""
    type = filters.CharFilter('type')
    store = filters.CharFilter('store')

    class Meta:
        models = Article
        fields = ('type', 'store')