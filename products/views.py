import logging
import json

from ipware import get_client_ip

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Order
from .utils import send_payu_order
from . import serializers

logger = logging.getLogger(__name__)


class ProductListView(ListView):
    model = Product
    context_object_name = "products"


class ProductDetailView(DetailView):
    template_name = 'confirm_purchase.html'
    queryset = Product.objects.all()


def buy_click(request, product_id):

    logger.debug('about to buy the product...')

    product = get_object_or_404(Product, pk=product_id, is_available=True)

    customer_ip, _ = get_client_ip(request)

    if not customer_ip:
        logger.debug('Real customer IP was not received')
        customer_ip = '127.0.0.1'

    order = Order(
        user=request.user,
        product=product,
        customer_ip=customer_ip,
    )

    order.save()

    url = send_payu_order(order=order, request=request)
    print('the returned URL is ', url)

    if url:
        logger.debug(f'Redirecting to {url}')
        return redirect(url)
    else:
        logger.debug(f'No URL returned')
        raise Http404()


@csrf_exempt
def notify_payment_view(request):
    print('')
    logger.debug('notify_payment_view')
    if request.method == 'POST':
        print(f'the request POST body == {request.body}')
        serializer = serializers.StatusSerializer(
            data=json.loads(request.body))


def purchases(request):

    logger.debug('purchases view')
    my_orders = Order.objects.all().filter(user=request.user).order_by('-id')

    return render(request, "purchase_history.html", context={'orders': my_orders})
