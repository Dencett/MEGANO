from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _


def profile_directory_path(instance: "User", filename):
    return "profiles/{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(_("Номер телефона"), max_length=11, default="")
    residence = models.CharField(
        _("Город проживания"),
        max_length=100,
    )
    address = models.TextField(_("Адрес"), max_length=500, blank=True)
    avatar = models.FileField(_("Аватар"), null=True, blank=True, upload_to=profile_directory_path)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
