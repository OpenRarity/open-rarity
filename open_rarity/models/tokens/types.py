from typing import NewType, TypedDict, Union

AttributeValue = str | int | float


class MetadataAttribute(TypedDict):
    name: str
    value: str | int | float
    display_type: str | None


class TokenData(TypedDict):
    token_identifier: str
    token_standard: str
    metadata: list[MetadataAttribute]
