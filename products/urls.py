from django.urls import path, include

from .views import ProductDetailView, \
    buy_click, notify_payment_view, purchases

urlpatterns = [
    path(
        'confirm-purchase/<pk>/',
        ProductDetailView.as_view(),
        name='confirm-purchase'
    ),
    path(
        'buy/<product_id>/',
        buy_click,
        name='buy-click',
    ),
    path(
        'notify',
        notify_payment_view,
        name='notify-payments',
    ),
    path(
        'my-purchases/',
        purchases,
        name='purchases',
    ),
]
