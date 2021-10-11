from django.urls import path, include
from feed import views
from rest_framework.routers import DefaultRouter

app_name = 'feed'

router = DefaultRouter()
router.register(r'article', views.ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('deletearticles', views.DeleteSeveralArticlesView.as_view())
]