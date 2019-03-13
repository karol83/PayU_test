from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ForeignKey, CASCADE
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from products.models import Product


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(
        _("Name of User"),
        blank=True,
        max_length=255
    )
    products = ForeignKey(
        Product,
        blank=True,
        null=True,
        on_delete=CASCADE,
        verbose_name=(_('Purchased Products'))
    )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_user_products(self):
        return self.products
