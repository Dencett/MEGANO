class MeganoOrder:
    def __init__(self, identify_number: int, cart_number: int, price: float):
        self.identify_number = identify_number
        self.cart_number = cart_number
        self.price = price


class ValidationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class VerificationFailed(Exception):
    pass


class TooManyRequests(Exception):
    pass
