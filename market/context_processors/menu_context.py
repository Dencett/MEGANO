from django.core.cache import cache
from django.http import HttpRequest

from products.models import Category


def categories_menu(request: HttpRequest):
    """
    Контекстный процессор добавления дерева Категорий в список 'context_processors'
    с оптимизацией кеширования данных

    doc: https://docs.djangoproject.com/en/4.2/ref/templates/api/#writing-your-own-context-processors
    """

    cache_key = "categories_data_export"
    categories_list = cache.get(cache_key)

    if categories_list is None:
        categories_list = Category.objects.select_related("parent").order_by("pk").filter(is_active=True)
        cache.set(cache_key, categories_list)

    def menu(objects, parent=None):
        """Функция создания дерева Категорий"""

        _menu = []

        for category in objects:
            if category.parent == parent:
                submenu = menu(objects, category)
                _menu.append({"category": category, "submenu": submenu})

        return _menu

    return {"menu": menu(categories_list)}
