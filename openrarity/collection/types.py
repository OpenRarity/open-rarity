from typing_extensions import NotRequired, TypedDict


class AttributeStatistic(TypedDict):
    """Statistics dictionary for just a (name, value) attributes pair."""

    name: str
    value: float | int | str
    count: int
    probability: NotRequired[float]
    ic: NotRequired[float]
    entropy: NotRequired[float]


__all__ = ["AttributeStatistic"]
