from django.core.management import BaseCommand
from django.core import management


class Command(BaseCommand):
    """
    Команда для массового создания фикстур.
    """

    def handle(self, *args, **kwargs):
        fixtures_dict = {
            # "contenttypes": "0-contenttypes.json",
            # "auth": "00-groups_and_permissions.json",
            "profiles.user": "01-users.json",
            "shops.shop": "04-shops.json",
            "products.category": "05-category.json",
            "products.tag": "06-tags.json",
            "products.product": "07-products.json",
            "shops.offer": "08-offers.json",
            "products.detail": "09-details.json",
            "products.productimage": "10-productimages.json",
            "products.productdetail": "11-productdetails.json",
            "products.review": "12-reviews.json",
        }
        for model_name, file_name in fixtures_dict.items():
            management.call_command("dumpdata", model_name, output=file_name, indent=4)
