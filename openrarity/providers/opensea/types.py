from typing import TypedDict


class TokenTrait(TypedDict):
    trait_type: str
    value: str | float | int
    display_type: str | None
    max_value: int | None
    trait_count: int
    order: None


class TokenAsset(TypedDict):
    token_id: str
    traits: list[TokenTrait]
