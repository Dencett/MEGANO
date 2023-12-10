from cart.services.cart_service import AnonimCartService
from .models import ProductPromo


class CartDiscount:
    def __init__(self, cart: "AnonimCartService"):
        self.cart = cart

    def get_sum(cls):
        """Метод определения размера скидки"""
        return 100


def get_all_products_in_set(model: ProductPromo):
    all_products = []
    all_products += list(model.products.all())
    for category in model.categories.all():
        children = category.children.all()
        if children:
            for child in children:
                all_products += list(child.product_set.all())
        all_products += list(category.product_set.all())
    return all_products
