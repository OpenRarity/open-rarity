from typing_extensions import NotRequired, TypedDict

AttributeStatistic = TypedDict(
    "AttributeStatistic",
    {
        "name": str,
        "value": float | int | str,
        "attribute.token_count": int,
        "attribute.supply": int,
        "metric.probability": NotRequired[float],
        "metric.information": NotRequired[float],
        "entropy": NotRequired[float],
    },
)
__all__ = ["AttributeStatistic"]
