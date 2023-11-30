from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product, Category


class CartPromo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование правила на корзину"))
    items_from = models.IntegerField(verbose_name=_("кол-во товаров в корзине от"))
    items_to = models.IntegerField(verbose_name=_("кол-во товаров в корзине до"))
    price_from = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("общая стоимость корзины от"))
    price_to = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("общая стоимость корзины до"))
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("размер скидки в рублях"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        verbose_name = _("правило скидки на корзину")
        verbose_name_plural = _("правила скидок на корзину")

    def __str__(self) -> str:
        return f"Правило на карзину (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"


class SetPromo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование набора"))
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

    class Meta:
        verbose_name = _("правило скидки на набор")
        verbose_name_plural = _("правила скидок на набор")

    def __str__(self) -> str:
        return f"Правило на набор (pk={self.pk}, name={self.name!r}, value={self.value!r}руб)"


class Promo(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("наименование скидки"))
    description = models.TextField(max_length=1024, verbose_name=_("описание скидки"))
    value = models.IntegerField(
        verbose_name=_("размер скидки в процентах"), validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    categories = models.ManyToManyField(Category, blank=True, related_name="promos", verbose_name=_("категории"))
    products = models.ManyToManyField(Product, blank=True, related_name="promos", verbose_name=_("товары"))
    sets = models.ManyToManyField(SetPromo, blank=True, related_name="promos", verbose_name=_("наборы"))
    carts = models.ManyToManyField(CartPromo, blank=True, related_name="promos", verbose_name=_("правила на корзину"))
    weight = models.FloatField(
        unique=True, verbose_name=_("вес скидки"), validators=[MinValueValidator(0.01), MaxValueValidator(1.00)]
    )
    active_from = models.DateTimeField(verbose_name=_("действует от "))
    active_to = models.DateTimeField(verbose_name=_("действует до "))

    class Meta:
        verbose_name = _("скидка")
        verbose_name_plural = _("скидки")

    def __str__(self) -> str:
        return f"Скидка(pk={self.pk}, name={self.name!r})"
