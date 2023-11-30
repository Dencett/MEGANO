from decimal import Decimal

from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product, Category


class CartPromo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование скидки на корзину"))
    description = models.TextField(max_length=1024, blank=True, verbose_name=_("описание скидки на корзину"))
    items_from = models.IntegerField(null=True, blank=True, verbose_name=_("кол-во товаров в корзине от"))
    items_to = models.IntegerField(null=True, blank=True, verbose_name=_("кол-во товаров в корзине до"))
    price_from = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("общая стоимость корзины от")
    )
    price_to = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("общая стоимость корзины до")
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки в рублях"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    weight = models.FloatField(
        unique=True, verbose_name=_("вес скидки"), validators=[MinValueValidator(0.01), MaxValueValidator(1.00)]
    )
    active_from = models.DateTimeField(null=True, blank=True, verbose_name=_("действует от "))
    active_to = models.DateTimeField(null=True, blank=True, verbose_name=_("действует до "))
    is_active = models.BooleanField(default=False, verbose_name=_("скидка активна"))

    class Meta:
        verbose_name = _("скидка на корзину")
        verbose_name_plural = _("скидки на корзину")
        constraints = [
            models.CheckConstraint(check=Q(items_from__lte=F("items_to")), name="items_from_lte_items_to"),
            models.CheckConstraint(check=Q(price_from__lte=F("price_to")), name="price_from_lte_price_to"),
            models.CheckConstraint(check=Q(active_from__lte=F("active_to")), name="cartpromo_date_from_lte_date_to"),
        ]

    def __str__(self) -> str:
        return f"Скидка на корзину (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"


class SetPromo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование скидки на набор"))
    description = models.TextField(max_length=1024, blank=True, verbose_name=_("описание скидки на набор"))
    products = models.ManyToManyField(
        Product, blank=True, related_name="products_set", verbose_name=_("набор товаров")
    )
    categories = models.ManyToManyField(
        Category, blank=True, related_name="categories_set", verbose_name=_("набор категорий")
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки в рублях"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    weight = models.FloatField(
        unique=True, verbose_name=_("вес скидки"), validators=[MinValueValidator(0.01), MaxValueValidator(1.00)]
    )
    active_from = models.DateTimeField(null=True, blank=True, verbose_name=_("действует от "))
    active_to = models.DateTimeField(null=True, blank=True, verbose_name=_("действует до "))
    is_active = models.BooleanField(default=False, verbose_name=_("скидка активна"))

    class Meta:
        verbose_name = _("скидка на наборы продуктов и/или категорий")
        verbose_name_plural = _("скидки на наборы продуктов и/или категорий")
        constraints = [
            models.CheckConstraint(check=Q(active_from__lte=F("active_to")), name="setpromo_date_from_lte_date_to"),
        ]

    def __str__(self) -> str:
        return (
            f"Cкидка на наборы продуктов и/или категорий (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"
        )


class ProductPromo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование скидки"))
    description = models.TextField(max_length=1024, blank=True, verbose_name=_("описание скидки"))
    value = models.IntegerField(
        verbose_name=_("размер скидки в процентах"), validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    categories = models.ManyToManyField(
        Category, blank=True, related_name="categories_promos", verbose_name=_("категории")
    )
    products = models.ManyToManyField(Product, blank=True, related_name="products_promos", verbose_name=_("товары"))
    weight = models.FloatField(
        unique=True, verbose_name=_("вес скидки"), validators=[MinValueValidator(0.01), MaxValueValidator(1.00)]
    )
    active_from = models.DateTimeField(null=True, blank=True, verbose_name=_("действует от "))
    active_to = models.DateTimeField(null=True, blank=True, verbose_name=_("действует до "))
    is_active = models.BooleanField(default=False, verbose_name=_("скидка активна"))

    class Meta:
        verbose_name = _("скидка на продукт(ы) и/или категорию(ии)")
        verbose_name_plural = _("скидки на продукт(ы) и/или категорию(ии)")
        constraints = [
            models.CheckConstraint(
                check=Q(active_from__lte=F("active_to")), name="product_promo_date_from_lte_date_to"
            ),
        ]

    def __str__(self) -> str:
        return f"Cкидка на продукт(ы) и/или категорию(ии)(pk={self.pk}, name={self.name!r}, value={self.value!r}%)"
