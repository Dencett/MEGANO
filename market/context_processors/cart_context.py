from django.conf import settings
from typing import Dict
from django.http import HttpRequest


def cart_size_context_processor(request: HttpRequest) -> Dict[str, str]:
    """
    Контекстный процессор добавления текущего размера корзины
    """

    size = request.session.get(settings.CART_SIZE_SESSION_KEY)
    if not size:
        size = 0
    return {"cart_size": size}
