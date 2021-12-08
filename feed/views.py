from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import permissions, status, generics

from django.shortcuts import get_object_or_404
from feed import models, serializers, filters


class ArticleViewSet(viewsets.ModelViewSet):
    """Manage article viewset"""
    permission_classes = (permissions.AllowAny,)
    queryset = models.Article.objects.all().order_by('-id')

    filter_backends = (DjangoFilterBackend,)
    filter_class = filters.ArticleFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.GetArticleSerializer
        return serializers.ArticleSerializer


class DeleteSeveralArticlesView(APIView):
    """Rate order"""
    serializer_class = serializers.DeleteSeveralArticlesSerializer

    def post(self, request):
        """Write review"""
        serializer = serializers.DeleteSeveralArticlesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            articles = serializer.validated_data['articles']
            for i in articles:
                article = models.Article.objects.filter(id=i).first()
                print("Item", article)
                if article:
                    article.delete()
                else:
                    continue
            return Response({"detail": "Deleted successfully"})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

