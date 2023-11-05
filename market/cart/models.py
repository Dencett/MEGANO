from django.db import models
from django.utils.translation import gettext_lazy as _


class UserOfferCart(models.Model):
    """Модель для упаковки товара с определенным количеством
    Если поле is_active = True то модель используется для текущей корзины пользователя.
    Совокупность моделей с is_active = True, будет являться текущей пользовательской корзиной.
    Если поле is_active = False, то модель будет использоваться для отображения модели уже оплаченного ЗАКАЗА.
    """

    offer = models.ForeignKey(to="shops.Offer", on_delete=models.CASCADE)
    user = models.ForeignKey(to="profiles.User", on_delete=models.CASCADE, related_name="carts")
    amount = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("запись корзины")
        verbose_name_plural = _("записи корзины")

    def __str__(self):
        return f"Пользователь {self.user} заказ {self.offer}"
