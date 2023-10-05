from typing import Tuple, Any, Dict, Generator, List

from django.db.models import QuerySet, Count, F, Q

from catalog.common import parse_price


class Params:
    def __init__(self, **kwargs) -> None:
        self.__items: Dict = kwargs

    def update(self, data: Dict | "Params", **kwargs) -> None:
        if isinstance(data, Params):
            self.__items.update(data.__items)

        elif isinstance(data, Dict):
            self.__items.update(data)

        else:
            raise TypeError(f"Wrong type data: `{type(data)}`. It's must be {self.__class__.__name__} or dict")

        if kwargs:
            self.__items.update(**kwargs)

    def get(self, key: Any, default: Any | None = None) -> Any:
        return self.__items.get(key, default)

    def pop(self, key: Any, default: None = None) -> Any:
        if key in self.__items:
            return self.__items.pop(key)

        return default

    def popitems(self, *keys) -> List:
        result = []

        for key in keys:
            value = self.pop(key)

            if value:
                result.append(value)

        return result

    def to_list(self) -> List[str]:
        if self:
            return [f"{key}={value}" for key, value in self.__items.items()]

        return []

    def to_dict(self) -> Dict[str, str]:
        return self.__items

    def to_string(self, first_char: str | None = None) -> str:
        if self:
            return first_char + "&".join(self.to_list()) if first_char else "&".join(self.to_list())

        return ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_list()})"

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> bool:
        return bool(self.__items)

    def __getitem__(self, item: Any) -> Any:
        return self.__items.__getitem__(item)

    def __setitem__(self, key: Any, value: Any) -> None:
        return self.__items.__setitem__(key, value)

    def __add__(self, other) -> "Params":
        if isinstance(other, Params):
            self.__items.update(other.__items)
            return self

        if isinstance(other, dict):
            self.__items.update(other)
            return self

        raise ValueError(f"`{other}` must be {self.__class__.__name__} or dict")

    def __iadd__(self, other) -> "Params":
        return self.__add__(other)

    def __contains__(self, value) -> bool:
        return value in self.__items


class Filter:
    default_price_from: float = 10.00
    default_price_to: float = 1000.00

    def __init__(self, params: Params) -> None:
        self.params = params

    def __price_filter(
        self,
        start_price: float,
        stop_price: float,
        field: str | None = None,
    ) -> Dict[str, Tuple[float, float]]:
        """
        Offer price filer
        """
        if not field:
            field = "price"

        return {f"{field}__range": (start_price, stop_price)}

    def __delivery_filter(self, field: str | None = None) -> Dict[str, str]:
        """
        Offer delivery filer
        """
        if not field:
            field = "delivery_method"

        return {field: "FREE"}

    def __product_search_filter(
        self,
        value: str,
        fields: List[str] | Tuple[str, str] | None = None,
    ) -> Q:
        """
        Product search filer
        """
        if not fields:
            fields = "about", "name"

        return Q(**{f"product__{fields[0]}__contains": value}) | Q(**{f"product__{fields[1]}__contains": value})

    def __category_available_filter(self) -> Dict[str, bool]:
        """
        Category available filter
        """
        return {
            "product__category__is_active": True,
            "product__category__archived": False,
        }

    def __category_filter(self, value: str) -> Dict[str, Any]:
        """
        Product category filter
        """
        return {"product__category__pk": value}

    def __remain_filter(self, field: str | None = None) -> Dict[str, int]:
        """
        Offer remain filter
        """
        if not field:
            field = "remains"

        return {f"{field}__gte": 1}

    def __tag_filter(self, value: str, field: str | None = None) -> Dict[str, str]:
        """
        Tag id filter
        """
        if not field:
            field = "product__tags__pk__contains"

        return {field: value}

    def filter_offer(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        if "price" in self.params:
            prices = parse_price(self.params.get("price"))

            if prices:
                start_price = prices[0]
                stop_price = prices[1]

                filter_.update(self.__price_filter(start_price, stop_price, "price"))

        if "free_delivery" in self.params:
            filter_.update(self.__delivery_filter("delivery_method"))

        if "remains" in self.params:
            filter_.update(self.__remain_filter("remains"))

        return queryset.filter(**filter_)

    def filter_prodict(self, queryset: QuerySet) -> QuerySet:
        filter_args = []

        search_or_title_value = self.params.get("title", self.params.get("search"))

        if search_or_title_value:
            filter_args.append(self.__product_search_filter(search_or_title_value))

        return queryset.filter(*filter_args)

    def filter_category(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        category_id = self.params.get("category_id")

        if category_id:
            filter_.update(self.__category_filter(category_id))

        filter_.update(self.__category_available_filter())

        return queryset.filter(**filter_)

    def filter_tags(self, queryset: QuerySet) -> QuerySet:
        filter_: Dict[str, Any] = {}

        tag_id = self.params.get("tag_id")

        if tag_id:
            filter_.update(self.__tag_filter(tag_id))

        return queryset.filter(**filter_)


class Sorter:
    default_sort = "pk"

    sort_types = {
        "famous": "Популярности",
        "price": "Цене",
        "review": "Отзывам",
        "recency": "Новизне",
    }

    def get_items(self) -> Generator[Tuple[str, str], None, None]:
        for name, title in self.sort_types.items():
            yield name, title

    def sort(
        self,
        queryset: QuerySet,
        sort: str | None = None,
        desc: str | None = None,
    ) -> QuerySet:
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
