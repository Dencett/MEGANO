from django.db import models
from django.utils.translation import gettext_lazy as _


class Shop(models.Model):
    """Магазин"""

    class Meta:
        verbose_name = _("магазин")
        verbose_name_plural = _("магазины")

    name = models.CharField(max_length=512, verbose_name=_("название"))
    products = models.ManyToManyField(
        "products.Product",
        through="Offer",
        related_name="shops",
        verbose_name=_("товары в магазине"),
    )


class Offer(models.Model):
    """Предложение магазина"""

    class Meta:
        verbose_name = _("предложение магазина")
        verbose_name_plural = _("предложения магазина")

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
