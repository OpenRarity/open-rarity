from typing import TypedDict

AttributeName = str
AttributeValue = str | int | float


class MetadataAttribute(TypedDict):
    name: str
    value: str | int | float
    display_type: str | None


class RawToken(TypedDict):
    token_id: int | str
    attributes: list[MetadataAttribute]


class TokenIdMetadataAttr(MetadataAttribute):
    token_id: int


class TokenData(TypedDict):
    token_id: int | str
    attributes: list[MetadataAttribute]


class RankedToken(TypedDict):
    token_id: int | str
    rank: int
    scores: dict


TokenSchema = dict[AttributeName, int]
