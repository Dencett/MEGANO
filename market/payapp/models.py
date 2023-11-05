from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class OrderPayStatus(models.Model):
    order = models.ForeignKey(
        to="orders.Order", related_name="payrecords", verbose_name=_("Заказ"), on_delete=models.CASCADE
    )
    answer_from_api = models.JSONField(verbose_name=_("Ответ сервиса оплаты"), null=True)
    created_at = models.DateTimeField(verbose_name=_("Дата выполнения"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("история оплаты заказа")
        verbose_name_plural = _("истории оплаты заказа")


# class TestOrder(models.Model):
#     number = models.IntegerField(verbose_name=_("Номер заказа"))
#     price = models.DecimalField(verbose_name=_("Цена заказа"), max_digits=8, decimal_places=2)
#     status_payed = models.BooleanField(default=False)
