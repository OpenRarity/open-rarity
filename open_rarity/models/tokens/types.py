from typing_extensions import NotRequired, TypedDict

AttributeName = str
AttributeValue = str | int | float


class MetadataAttribute(TypedDict):
    name: str
    value: str | int | float
    display_type: NotRequired[str | None]


class RawToken(TypedDict):
    token_id: int | str
    attributes: list[MetadataAttribute]


class TokenIdMetadataAttr(MetadataAttribute):
    token_id: int


class TokenAttributeStatistic(TokenIdMetadataAttr):
    count: int
    probability: float
    ic: float
    entropy: NotRequired[float]
    unique_trait_count: NotRequired[int]


class RankedToken(TypedDict):
    token_id: int | str
    rank: int
    metrics: list[TokenAttributeStatistic]


TokenSchema = dict[AttributeName, int]

__all__ = [
    "AttributeName",
    "AttributeValue",
    "MetadataAttribute",
    "RawToken",
    "TokenIdMetadataAttr",
    "TokenAttributeStatistic",
    "RankedToken",
    "TokenSchema",
]
