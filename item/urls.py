from django.urls import path, include
from item import views
from rest_framework.routers import SimpleRouter

app_name = 'item'

router = SimpleRouter()
router.register(r'itemcategory', views.ItemCategoryViewSet)
router.register(r'item', views.ItemViewSet, basename='items')
router.register(r'getitem', views.GetItemViewSet)

router.register(r'userfavouriteitem', views.UserFavouriteItemViewSet)
router.register(r'itemadditive', views.ItemAdditiveViewSet)
router.register(r'cart', views.CartViewSet)
router.register(r'clientorder', views.ClientOrderViewSet)
router.register(r'rateorder', views.OrderRateViewSet)
router.register(r'itemwithquantity', views.ItemWithQuantityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statusupdate/<int:pk>', views.StatusUpdateView.as_view()),
    path('getclientorder/', views.GetClientOrderView.as_view()),
    path('removecartitem/', views.RemoveItem.as_view()),
    path('removeitem/', views.RemoveCartItem.as_view()),

    path('orderaction/', views.OrderActionView.as_view()),
    path('scoreaction/', views.ScoreActionView.as_view()),
    path('paymentaction/', views.PaymentActionView.as_view()),
    path('report/', views.OrderReportView.as_view()),
    path('taketogether/<int:pk>', views.AddTakeTogetherView.as_view()),
    path('deleteitems', views.DeleteSeveralItemsView.as_view()),
    path('itemshare/<int:pk>', views.ItemShareLinkView.as_view(), name='itemshare'),
    path('deletecarts', views.DeleteCartsView.as_view()),
    path('payment_result', views.PaymentResult.as_view()),
    path('payment_result/<str:pg_order_id>', views.PaymentResultDetail.as_view())
]