from cart.services.cart_service import AnonimCartService


class CartDiscount:
    def __init__(self, cart: "AnonimCartService"):
        self.cart = cart

    def get_sum(cls):
        """Метод определения размера скидки"""
        return 100
