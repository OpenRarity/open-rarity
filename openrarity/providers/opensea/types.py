from typing import TypedDict


class TokenTrait(TypedDict):
    """This class shows all the metadata of a trait. Traits are specific properties each NFT has."""
    trait_type: str
    value: str | float | int
    display_type: str | None
    max_value: int | None
    trait_count: int
    order: None


class TokenAsset(TypedDict):
    """This class represents a list of traits of a token."""
    token_id: str
    traits: list[TokenTrait]
