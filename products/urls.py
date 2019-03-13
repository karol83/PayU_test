from django.urls import path, include

from .views import ProductDetailView

urlpatterns = [
    path(
        'confirm-purchase/<pk>/',
        ProductDetailView.as_view(),
        name='confirm-purchase'),
]
