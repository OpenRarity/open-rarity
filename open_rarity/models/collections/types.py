from typing import TypedDict

from open_rarity.models.tokens import MetadataAttribute


class TokenInput(TypedDict):
    token_id: int | str
    attributes: list[MetadataAttribute]


class AttributeCounts(TypedDict):
    name: str
    value: int | float | str
    count: int
