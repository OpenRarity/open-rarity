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
    token_supply: NotRequired[dict[str | int, int]]


class TokenAttribute(TypedDict):
    token_id: int
    name: str
    value: str | int | float
    display_type: NotRequired[str | None]


class AttributeStatistic(MetadataAttribute):
    count: int
    probability: NotRequired[float]
    ic: NotRequired[float]
    entropy: NotRequired[float]


class TokenStatistic(TokenAttribute):
    count: int
    probability: float
    ic: float
    entropy: NotRequired[float]
    unique_trait_count: NotRequired[int]
    max_trait_ic: NotRequired[float]


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
    "TokenId",
    "TokenStatistic",
]
