from django.apps import AppConfig

# from django.core import management


class CartConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"
    #
    # def ready(self):
    #     management.call_command("clearsessions")
