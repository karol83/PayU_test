# -*- coding: utf-8 -*-
import uuid

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings


class Product(models.Model):
    name = models.CharField(_(u'Name'), max_length=127)
    desc = models.CharField(_(u'Description'), max_length=255)
    price = models.PositiveIntegerField(_(u'Price'))
    is_available = models.BooleanField(_(u'Available'), default=False)

    def __unicode__(self):
        return f"{self.name} - {self.price}"

    def __str__(self):
        return f"{self.name}: {self.desc} - ${self.price} | {self.is_available}"

    def get_price(self):
        price = self.price/100
        return price


PAYMENT_STATUS = (
    ('NEW', _('NEW')),
    ('PENDING', _('PENDING')),
    ('CANCELED', _('CANCELED')),
    ('COMPLETED', _('COMPLETED')),
    ('REJECTED', _('REJECTED'))
)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_(u'user')

    )
    product = models.ForeignKey(
        Product,
        verbose_name=_(u'Product name'),
        on_delete=models.CASCADE,
    )
    order_id = models.UUIDField(
        verbose_name=_(u'Transaction id'),
        editable=False,
        default=uuid.uuid4
    )
    customer_ip = models.GenericIPAddressField(
        _(u'Client Ip Address'),
        default='127.0.0.1',
    )
    status = models.CharField(
        verbose_name=_(u'Payment status'),
        max_length=9,
        choices=PAYMENT_STATUS,
        default='NEW'
    )
    status_date = models.DateField(
        verbose_name=_(u'Payment confirmation date'),
        blank=True,
        null=True,
        default=None
    )

    def add_purches_to_user(self):
        self.user.products += self.product
        self.user.save()

    def get_product_name(self):
        return self.product.name

    def get_product_price(self):
        return self.product.price / 100

    def get_product_description(self):
        return self.product.desc
