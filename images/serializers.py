from rest_framework import serializers, exceptions
from images import models


class ImageSerializer(serializers.ModelSerializer):
    """Image serializer"""
    class Meta:
        model = models.ImageUpload
        fields = ('id', 'image')
        read_only_fields = ('id',)