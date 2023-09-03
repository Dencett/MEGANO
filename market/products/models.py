from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Продукт"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    details = models.ManyToManyField("Detail", through="ProductDetail", verbose_name=_("характеристики"))


class Detail(models.Model):
    """Свойство продукта"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductDetail(models.Model):
    """Значение свойства продукта"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    detail = models.ForeignKey(Detail, on_delete=models.CASCADE)
    value = models.CharField(max_length=128, verbose_name=_("значение"))


class Category(models.Model):
    """Категория продукта"""

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    name = models.CharField(max_length=128, unique=True, verbose_name=_("наименование"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("дата последнего изменения"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))

    parent = models.ForeignKey("self", null=True, verbose_name=_("родитель"), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Категория(pk={self.pk}, name={self.name!r})"
