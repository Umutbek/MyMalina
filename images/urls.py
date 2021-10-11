from django.urls import path, include
from rest_framework.routers import DefaultRouter
from images import views

app_name = 'images'

router = DefaultRouter()
router.register(r'image/upload', views.UploadImageViewSet)


urlpatterns = [
    path('', include(router.urls)),
]