import datetime

from profiles.models import User, UserProductHistory
from products.models import Product

HISTORY_SIZE = 9


class History:
    def __init__(self, user: User):
        self.user = user
        self.products_in_history = list(self.get_products_in_user_history(user))

    @staticmethod
    def get_products_in_user_history(user: User, number: int = HISTORY_SIZE):
        """Получение отсортированного по времени списка товаров из истории просмотров"""
        history = user.product_in_history.order_by("userproducthistory").all()[:number]
        return history

    def product_in_user_history(self, product: Product):
        """Проверка товара в истории"""
        return product in self.products_in_history

    def make_record(self, product: Product):
        """Добавление товара в историю"""
        if product == self.products_in_history[0]:
            return
        if self.product_in_user_history(product):
            UserProductHistory.objects.filter(product=product, user=self.user).update(time=datetime.datetime.utcnow())
            return
        if len(self.products_in_history) == HISTORY_SIZE - 1:
            last_product = self.products_in_history[-1]
            UserProductHistory.objects.filter(product=last_product, user=self.user).update(product=product)
        elif len(self.products_in_history) < HISTORY_SIZE - 1:
            record = UserProductHistory(product=product, user=self.user)
            record.save()
        else:
            self.validate_db_history()
            self.make_record(product)

    def validate_db_history(self):
        """Удаление избыточных записей с БД"""
        excess_products = self.products_in_history[HISTORY_SIZE - 1 :]  # noqa
        self.user.product_in_history.remove(excess_products)

    def length(self):
        """Возвращает количество записей в истории"""
        return len(self.products_in_history)
