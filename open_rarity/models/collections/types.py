from typing_extensions import NotRequired, TypedDict

from open_rarity.models.tokens import MetadataAttribute


class TokenInput(TypedDict):
    token_id: int | str
    attributes: list[MetadataAttribute]


class AttributeCounted(TypedDict):
    name: str
    value: int | float | str
    count: int


class AttributeStatistic(AttributeCounted):
    probability: float
    ic: float
    entropy: NotRequired[float]


__all__ = ["TokenInput", "AttributeCounted", "AttributeStatistic"]
