import random
from typing import List

from django.core.cache import cache
from django.http import HttpRequest

from products.models import Product


def product_placeholders(request: HttpRequest):
    """
    Контекстный процессор добавления случайных заполнителей строки поиска
    """
    fields = ["name"]
    cache_key = "products"
    products: List[Product] = cache.get(cache_key)

    if products is None:
        products = Product.objects.order_by("pk").only(*fields)
        cache.set(cache_key, products)

    return {"search_placeholder": random.choice(products).name}
