from rest_framework import viewsets, permissions, status, generics, authentication
from rest_framework.response import Response
from images import models, serializers


class UploadImageViewSet(viewsets.ModelViewSet):
    """Upload image"""
    permission_classes = (permissions.AllowAny,)
    queryset = models.ImageUpload.objects.all()
    serializer_class = serializers.ImageSerializer