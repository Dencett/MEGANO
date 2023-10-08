from django.db import models


class CatalogTestmodel(models.Model):
    offer = models.ForeignKey(to="shops.Offer", on_delete=models.CASCADE)
    user = models.ForeignKey(to="profiles.User", on_delete=models.CASCADE, related_name="test")
    amount = models.IntegerField(default=1)


# from django.db import models

# Create your models here.
