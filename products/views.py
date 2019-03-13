from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Product


class ProductListView(ListView):
    model = Product
    context_object_name = "products"


class ProductDetailView(DetailView):
    template_name = 'confirm_purchase.html'
    queryset = Product.objects.all()
