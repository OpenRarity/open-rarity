from typing_extensions import NotRequired, TypedDict


class AttributeStatistic(TypedDict):
    name: str
    value: float | int | str
    count: int
    probability: float
    ic: float
    entropy: NotRequired[float]


__all__ = ["AttributeStatistic"]
