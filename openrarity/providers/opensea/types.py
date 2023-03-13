from typing import TypedDict


class TokenTrait(TypedDict):
    """A class to represent `TokenTrait`."""
    trait_type: str
    value: str | float | int
    display_type: str | None
    max_value: int | None
    trait_count: int
    order: None


class TokenAsset(TypedDict):
    """A class to represent `TokenAsset`."""
    token_id: str
    traits: list[TokenTrait]
