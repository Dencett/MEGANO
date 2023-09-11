from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.validators import FileExtensionValidator


class Product(models.Model):
    """Продукт"""

    class Meta:
        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    details = models.ManyToManyField("Detail", through="ProductDetail", verbose_name=_("характеристики"))


class Detail(models.Model):
    """Свойство продукта"""

    class Meta:
        verbose_name = _("свойство продуктов")
        verbose_name_plural = _("свойства продуктов")

    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductDetail(models.Model):
    """Значение свойства продукта"""

    class Meta:
        verbose_name = _("значение свойства продуктов")
        verbose_name_plural = _("значения свойства продуктов")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    detail = models.ForeignKey(Detail, on_delete=models.CASCADE)
    value = models.CharField(max_length=128, verbose_name=_("значение"))


def category_icon_directory_path(instance: "Category", filename: str) -> str:
    return "img/icons/categories/{filename}".format(
        filename=filename,
    )


class Category(models.Model):
    """Категория продукта"""

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
        app_label = "products"

    name = models.CharField(max_length=128, unique=True, verbose_name=_("наименование"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("дата последнего изменения"))
    archived = models.BooleanField(default=False, verbose_name=_("архивировано"))
    is_active = models.BooleanField(default=True, verbose_name=_("активно"))
    parent = models.ForeignKey("self", blank=True, null=True, verbose_name=_("родитель"), on_delete=models.CASCADE)

    icon = models.FileField(
        null=True,
        blank=True,
        upload_to=category_icon_directory_path,
        verbose_name=_("иконка"),
        validators=[FileExtensionValidator(["svg", "img", "png"])],
    )

    def __str__(self) -> str:
        return f"Категория(pk={self.pk}, name={self.name!r})"
