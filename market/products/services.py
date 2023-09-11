from .models import Category
from django.core.cache import cache


def category_menu():
    """Функция получения дерева Категорий"""

    cache_key = "categories_data_export"
    categories_list = cache.get(cache_key)

    if categories_list is None:
        categories_list = Category.objects.all().order_by("pk").filter(is_active=True)
        cache.set(cache_key, categories_list)

    def menu(objects, parent=None):
        """Функция создания дерева Категорий"""

        _menu = []

        for category in objects:
            if category.parent == parent:
                submenu = menu(objects, category)
                _menu.append({"category": category, "submenu": submenu})

        return _menu

    return menu(categories_list) if categories_list else []
