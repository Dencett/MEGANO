from typing import Tuple, Any, Dict, Generator

from django.db.models import QuerySet, F, Count

from catalog.common import Params
from catalog.forms import CatalogFilterForm


class Filter:
    default_price_from: float = 10.00
    default_price_to: float = 1000.00

    def __init__(self, params: Params) -> None:
        self.__params = params

    def __extract_params_data(self) -> Dict:
        data = {}

        for field in CatalogFilterForm().fields:
            param_value = self.__params.get(field)

            if param_value:
                data[field] = param_value

        return data

    def build_params(self) -> Params:
        return Params(**self.__extract_params_data())

    @classmethod
    def parse_price(cls, price: str | None = None) -> Tuple[float, float] | None:
        if not price:
            return

        prices = price.split(";")

        if len(prices) != 2:
            return

        try:
            return float(prices[0]), float(prices[1])

        except ValueError:
            return

    def get_context_data(self) -> Dict[str, Any]:
        data = self.__extract_params_data()
        prices = self.parse_price(self.__params.get("price"))

        if prices:
            data["start_price"] = prices[0]
            data["stop_price"] = prices[1]

        data["default_price_from"] = self.default_price_from
        data["default_price_to"] = self.default_price_to

        return data

    def __price_filter(self) -> Dict[str, Tuple[float, float]]:
        """
        Offer price filer
        """
        start_price = self.get_context_data().get("start_price", self.default_price_from)
        stop_price = self.get_context_data().get("stop_price", self.default_price_to)

        return {"price__range": (start_price, stop_price)}

    def __delivery_filter(self) -> Dict[str, str]:
        """
        Offer delivery filer
        """
        return {"delivery_method": "REGULAR"}

    def __title_filter(self) -> Dict[str, str]:
        """
        Product title filer
        """
        return {"product__about__contains": self.__params.get("title")}

    def __category_filter(self) -> Dict[str, bool]:
        """
        Product category filter
        """
        return {"product__category__is_active": True, "product__category__archived": False}

    def __remain_filter(self) -> Dict[str, int]:
        """
        Offer remain filter
        """
        return {"remains__gte": 1}

    def filter_offer(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        if "price" in self.__params.items:
            filter_.update(self.__price_filter())

        if "free_delivery" in self.__params.items:
            filter_.update(self.__delivery_filter())

        if "remains" in self.__params.items:
            filter_.update(self.__remain_filter())

        return queryset.filter(**filter_)

    def filter_prodict(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        if "title" in self.__params.items:
            filter_.update(self.__title_filter())

        filter_.update(self.__category_filter())

        return queryset.filter(**filter_)


class Sorter:
    default_sort = "pk"
    default_sort_name = "famous"
    default_sort_desc = "on"

    sort_types = {
        "famous": "Популярности",
        "price": "Цене",
        "review": "Отзывам",
        "recency": "Новизне",
    }

    def __init__(self, params: Params) -> None:
        self.__params = params

    def build_params(self) -> Params:
        sort = self.__params.get("sort") or self.default_sort_name
        sort_desc = "on" if self.__params.get("sort_desc") == "on" else "off"

        return Params(sort=sort, sort_desc=sort_desc)

    def __get_items(self) -> Generator:
        for name, title in self.sort_types.items():
            yield name, title

    def get_context_data(self) -> Dict[str, str]:
        sort = self.__params.get("sort") or self.default_sort_name
        sort_desc = self.__params.get("sort_desc") or self.default_sort_desc

        return {
            "sort": sort,
            "sort_desc": sort_desc,
            "sort_items": self.__get_items(),
        }

    def sort(self, queryset: QuerySet) -> QuerySet:
        params = self.build_params()

        sort = params.get("sort")
        desc = params.get("sort_desc")

        if not sort:
            return queryset.order_by(self.default_sort)

        if sort == "famous":
            return self._sort_by_famous(queryset, desc)

        if sort == "price":
            return self._sort_by_price(queryset, desc)

        if sort == "review":
            return self._sort_by_review(queryset, desc)

        if sort == "recency":
            return self._sort_by_recency(queryset, desc)

    def _sort_by_famous(self, queryset: QuerySet, desc: str) -> QuerySet:
        return queryset.order_by(self.default_sort)  # TODO: добавить сортировку по популярности

    def _sort_by_price(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("price").desc()
        else:
            param = F("price").asc()

        return queryset.order_by(param)

    def _sort_by_review(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("review_count").desc()
        else:
            param = F("review_count").asc()

        return queryset.annotate(review_count=Count(F("product__review"))).order_by(param)

    def _sort_by_recency(self, queryset: QuerySet, desc: str) -> QuerySet:
        if desc == "on":
            param = F("product__manufacturer__modified_at").desc()
        else:
            param = F("product__manufacturer__modified_at").asc()

        return queryset.order_by(param)
