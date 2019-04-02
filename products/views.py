import logging
import json
import datetime

from ipware import get_client_ip

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.urls import reverse

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

    customer_ip, routable = get_client_ip(request)

    logger.debug(f'this {customer_ip} is routable: {routable}')

    if not customer_ip:
        logger.debug('Real customer IP was not received')
        customer_ip = '127.0.0.1'

    order = Order(
        user=request.user,
        product=product,
        customer_ip=customer_ip,
    )
    logger.debug(f'Order notify_url: {order.customer_ip}')
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

    logger.debug('notify payments view')
    if request.method == 'POST':
        logger.debug('POST')
        serializer = serializers.StatusSerializer(
            data=json.loads(request.body))

        if not serializer.is_valid():
            logger.exception(u"PayU: Unsupported data. {0}".format(
                force_text(request.body)))
            return HttpResponse('')

        try:
            logger.debug("Fetching order")
            order = Order.objects.get(
                external_id=serializer.validated_data['order']['extOrderId'])
        except Order.DoesNotExist:
            logger.exception(
                u"PayU: order does not exist. {0}".format(
                    force_text(request.body)))
            return HttpResponse('')

        if order.status != 'COMPLETED':
            logger.debug("Order.status was not completed yet!")
            with transaction.atomic():
                if serializer.validated_data['order']['status'] == 'COMPLETED':
                    logger.debug(f"The concerned order.status {order} is completed: {order.status}")
                    order.status = 'COMPLETED'
                    order.status_date = datetime.date.today()
                    order.save()
                    order.extend_subscription()
                elif serializer.validated_data['order']['status'] == 'PENDING':
                    logger.debug("ZWALIDOWANY order.status JEST PENDING")
                    pass
                else:
                    logger.debug(u"ZWALIDOWANY order.status = {0}".format(serializer.validated_data['order']['status']))
                    order.status = 'CANCELED'
                    order.status_date = datetime.date.today()
                    order.save()
        return HttpResponse('')


def purchases(request):

    logger.debug('purchases view')
    my_orders = Order.objects.all().filter(user=request.user).order_by('-id')

    return render(request, "purchase_history.html", context={'orders': my_orders})
