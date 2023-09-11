from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


def profile_directory_path(instance: "Profile", filename):
    return "profiles/{pk}/avatar/{filename}".format(
        pk=instance.user.pk,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    phone_number = models.CharField(max_length=11)
    residence = models.CharField(max_length=100)
    address = models.TextField(max_length=500, blank=True)
    avatar = models.FileField(null=True, blank=True, upload_to=profile_directory_path)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.user.username}"

    def get_username(self):
        return self.user.username
