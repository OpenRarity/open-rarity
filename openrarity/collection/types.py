from typing_extensions import NotRequired, TypedDict


class AttributeCounted(TypedDict):
    name: str
    value: float | int | str
    count: int


class AttributeStatistic(AttributeCounted):
    probability: float
    ic: float
    entropy: NotRequired[float]


__all__ = ["AttributeCounted", "AttributeStatistic"]
