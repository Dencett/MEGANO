from django.db import models


class UserOfferCART(models.Model):
    offer = models.ForeignKey(to="shops.Offer", on_delete=models.CASCADE)
    user = models.ForeignKey(to="profiles.User", on_delete=models.CASCADE, related_name="cart")
    amount = models.IntegerField(default=1)
