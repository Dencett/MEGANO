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
        related_query_name="shop",
        verbose_name=_("товары в магазине"),
    )

    def __str__(self) -> str:
        return f"Продавец (pk={self.pk}, name={self.name!r})"


class PaymentMethod(models.TextChoices):
    CARD = "CARD", _("Банковской картой")
    CASH = "CASH", _("Наличными")


class DeliveryMethod(models.TextChoices):
    FREE = "FREE", _("Бесплатная доставка")
    REGULAR = "REGULAR", _("Обычная доставка")
    EXPRESS = "EXPRESS", _("Экспресс доставка")


class Offer(models.Model):
    """Предложение магазина"""

    class Meta:
        verbose_name = _("предложение магазина")
        verbose_name_plural = _("предложения магазина")

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
    remains = models.PositiveIntegerField(verbose_name=_("остаток"))
    payment_method = models.CharField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name=_("способ оплаты"),
        max_length=128,
    )
    delivery_method = models.CharField(
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.REGULAR,
        verbose_name=_("способ доставки"),
        max_length=128,
    )
    quantity = models.IntegerField(default=0, verbose_name=_("количество"))

    def __str__(self) -> str:
        return f"Предложение (pk={self.pk}, shop={self.shop.name!r}), product={self.product.name!r}"
