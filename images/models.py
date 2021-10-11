from django.db import models
from images import imggenerate


class ImageUpload(models.Model):
    """Model to save all media of this project"""
    image = models.ImageField(null=True, upload_to=imggenerate.all_image_file_path)
