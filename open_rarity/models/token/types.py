from typing_extensions import NotRequired, TypedDict

AttributeName = str
AttributeValue = str | int | float
TokenId = int | str


class MetadataAttribute(TypedDict):
    name: str
    value: str | int | float
    display_type: NotRequired[str | None]


class RawToken(TypedDict):
    attributes: list[MetadataAttribute]
    properties: NotRequired[dict]


class TokenAttribute(MetadataAttribute):
    token_id: int


class AttributeStatistic(TokenAttribute):
    count: int
    probability: float
    ic: float
    entropy: NotRequired[float]
    unique_trait_count: NotRequired[int]


class RankedToken(TypedDict):
    token_id: int | str
    rank: int
    metrics: list[AttributeStatistic]


TokenSchema = dict[AttributeName, int]

__all__ = [
    "AttributeName",
    "AttributeValue",
    "MetadataAttribute",
    "RawToken",
    "TokenAttribute",
    "AttributeStatistic",
    "RankedToken",
    "TokenSchema",
]
