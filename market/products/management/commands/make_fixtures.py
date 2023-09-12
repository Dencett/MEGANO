from django.core.management import BaseCommand
from django.core import management


class Command(BaseCommand):
    """
    Create  test tg_bot_wardrobe_app
    """

    def handle(self, *args, **kwargs):
        fixtures_dict = {
            "shops.shop": "02-shops.json",
            "products.tag": "04-tags.json",
            "products.category": "05-category.json",
            "products.product": "06-products.json",
            "shops.offer": "07-offers.json",
            "products.detail": "09-details.json",
            "products.productimage": "10-productimages.json",
            "products.productdetail": "11-productdetails.json",
        }
        for model_name, file_name in fixtures_dict.items():
            management.call_command("dumpdata", model_name, output=file_name)
