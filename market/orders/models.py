from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from cart.models import UserOfferCart


class Order(models.Model):
    DELIVERY_TYPE_DICT = {
        "usually": "обычная доставка",
        "express": "экспресс-доставка",
    }

    DELIVERY_TYPE = [
        ("usually", "обычная доставка"),
        ("express", "экспресс-доставка"),
    ]

    PAYMENT_TYPES = [
        ("card", "онлайн картой"),
        ("random", "Онлайн со случайного чужого счета"),
    ]

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("дата создания заказа"),
    )
    city = models.CharField(
        max_length=50,
        verbose_name=_("Город доставки"),
    )
    address = models.CharField(max_length=260, verbose_name=_("адрес доставки"))
    carts = models.ManyToManyField(
        UserOfferCart,
        verbose_name=_("корзина"),
        help_text=_("товары в корзине выбранные пользователем"),
    )
    delivery_type = models.CharField(
        max_length=50,
        choices=DELIVERY_TYPE,
        default=DELIVERY_TYPE[0],
        verbose_name=_("метод доставки"),
    )
    payment_type = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPES,
        blank=False,
        default=PAYMENT_TYPES[0],
        verbose_name=_("способ оплаты"),
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("общая стоимость"),
    )

    class Meta:
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")

    def __str__(self):
        return f"{self.pk}{self.city}"

    def products_summ_price(self):
        total_price = self.carts.aggregate(total_price=Sum("offer__price"))
        convert_value = total_price["total_price"]
        return convert_value
