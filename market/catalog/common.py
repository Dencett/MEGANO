from typing import Dict, List, Any


class Params:
    def __init__(self, **kwargs) -> None:
        self.__items: Dict = {**kwargs}

    @property
    def items(self) -> Dict[str, str]:
        return self.__items

    def update(self, data: Dict | "Params" = None, **kwargs) -> None:
        if isinstance(data, Params):
            self.__items.update(data.__items)

        elif isinstance(data, Dict):
            self.__items.update(data)

        if kwargs:
            self.__items.update(**kwargs)

    def get(self, key: Any) -> Any:
        return self.__items.get(key)

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
        return [f"{key}={value}" for key, value in self.__items.items()]

    def to_dict(self) -> Dict[str, str]:
        return self.__items

    def to_string(self) -> str:
        return "&".join(self.to_list())

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

    def __add__(self, other) -> str:
        if isinstance(other, str):
            return self.to_string() + other

        if isinstance(other, Params):
            return self.to_string() + ("&" if self and other else "") + other.to_string()

        raise ValueError(f"`{other}` must be {self.__class__.__name__} or string")
