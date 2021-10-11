from django.urls import path, include
from user import views
from rest_framework.routers import DefaultRouter

app_name = 'user'

router = DefaultRouter()
router.register(r'store', views.StoreViewSet, basename='stores')
router.register(r'client', views.UserViewSet)
router.register(r'favouritestores', views.UserFavouriteStoreViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'subcategory', views.SubcategoryViewSet)
router.register(r'withdraw', views.WithDrawScoreViewSet)
router.register(r'address', views.AddressViewSet)
router.register(r'rating', views.RatingViewSet)
router.register(r'appprompt', views.AppPromptViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', views.RefreshTokenView.as_view()),
    path('login/', views.LoginAPI.as_view()),
    path('storelogin/', views.LoginAPI.as_view()),

    path('storelogin/', views.StoreLoginAPI.as_view()),
    path('getme/', views.GetMeView.as_view()),
    path('changepassword/', views.PasswordChangeView.as_view()),
    path('deliverycost/<int:pk>', views.GetDeliveryCostView.as_view()),
    path('getcode/', views.GetQrCodeView.as_view()),
    path('getpoints/', views.GetPointsView.as_view()),
    path('storeshare/<int:pk>', views.StoreShareLinkView.as_view(), name='storeshare')
]


