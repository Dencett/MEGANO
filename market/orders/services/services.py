from orders.models import Order


class OrderServices:
    def __init__(self, request):
        self.request = request

    def get_last_order(self) -> Order:
        return Order.objects.filter(carts__user_user_id=self.request.pk)
