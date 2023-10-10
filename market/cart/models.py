from django.db import models
from django.utils.translation import gettext_lazy as _


class UserOfferCart(models.Model):
    offer = models.ForeignKey(to="shops.Offer", on_delete=models.CASCADE)
    user = models.ForeignKey(to="profiles.User", on_delete=models.CASCADE, related_name="cart")
    amount = models.IntegerField(default=1)

    class Meta:
        verbose_name = _("запись корзины")
        verbose_name_plural = _("записи корзины")
