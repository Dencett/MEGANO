import datetime
from django.utils import timezone

from profiles.models import User, UserProductHistory
from products.models import Product

HISTORY_SIZE = 9


# class History:
#     def __init__(self, user: User):
#         self.user = user
#         self.products_in_history = list(self.get_products_in_user_history(user))
#
#     @staticmethod
#     def get_products_in_user_history(user: User, number: int = HISTORY_SIZE):
#         """Получение отсортированного по времени списка товаров из истории просмотров"""
#         history = user.product_in_history.order_by("userproducthistory").all()[:number]
#         return history
#
#     def product_in_user_history(self, product: Product):
#         """Проверка товара в истории"""
#         return product in self.products_in_history
#
#     def make_record(self, product: Product):
#         """Добавление товара в историю"""
#         if product == self.products_in_history[0]:
#             return
#         if self.product_in_user_history(product):
#            UserProductHistory.objects.filter(product=product, user=self.user).update(time=datetime.datetime.utcnow())
#             return
#         if len(self.products_in_history) == HISTORY_SIZE - 1:
#             last_product = self.products_in_history[-1]
#             UserProductHistory.objects.filter(product=last_product, user=self.user).update(product=product)
#         elif len(self.products_in_history) < HISTORY_SIZE - 1:
#             record = UserProductHistory(product=product, user=self.user)
#             record.save()
#         else:
#             self.validate_db_history()
#             self.make_record(product)
#
#     def validate_db_history(self):
#         """Удаление избыточных записей с БД"""
#         excess_products = self.products_in_history[HISTORY_SIZE - 1 :]  # noqa
#         self.user.product_in_history.remove(excess_products)
#
#     def length(self):
#         """Возвращает количество записей в истории"""
#         return len(self.products_in_history)


def is_product_in_history(user: User, product: Product):
    """Есть ли товар в истории просмотра пользователя"""
    return UserProductHistory.objects.filter(user=user, product=product).exists()


def get_history_length(user: User):
    """Возвращает количество записей в истории"""
    return UserProductHistory.objects.filter(user=user).count()


def get_latest_product(user: User):
    """Возвращает последний товар в истории"""
    latest_product = user.product_in_history.order_by("userproducthistory").first()
    return latest_product


def get_products_in_user_history(user: User, number: int = HISTORY_SIZE):
    """Получение отсортированного по времени списка товаров из истории просмотров"""
    history = user.product_in_history.order_by("userproducthistory").all()[:number]
    return history


def validate_user_history(user: User):
    history = (
        UserProductHistory.objects.filter(user=user).order_by("-time")[: HISTORY_SIZE - 1].values_list("id", flat=True)
    )
    UserProductHistory.objects.exclude(pk__in=list(history)).delete()


def make_record_in_history(user: User, product: Product, recurse=False):
    if not recurse:
        latest_product = get_latest_product(user)
        if latest_product == product:
            return
        if is_product_in_history(user, product):
            UserProductHistory.objects.filter(user=user, product=product).update(
                time=datetime.datetime.now(tz=timezone.get_current_timezone())
            )
            # time = datetime.datetime.now(tz=timezone.get_current_timezone())
            return
    history_length = get_history_length(user)
    if history_length == HISTORY_SIZE:
        record = UserProductHistory.objects.filter(user=user).order_by("-time").last()
        record.product = product
        record.save()
        return
    if history_length < HISTORY_SIZE:
        UserProductHistory(user=user, product=product).save()
        return
    if history_length > HISTORY_SIZE:
        validate_user_history(user)
        make_record_in_history(user, product, True)
