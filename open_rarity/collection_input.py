"""Ordered scoring inputs retain duplicate source traits."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class TraitInput:
    trait_type: str
    value: str | int | float | Decimal | None
    display_type: str | None = None


@dataclass(frozen=True)
class TokenInput:
    token_id: str
    traits: tuple[TraitInput, ...] = ()
    token_id_kind: Literal["evm", "raw"] = "evm"


@dataclass(frozen=True)
class CollectionInput:
    tokens: tuple[TokenInput, ...]


def parse_collection_json(text: str) -> CollectionInput:
    """Decode trait numbers as exact decimals, retaining ordered source entries."""
    import json

    def invalid(value):
        raise ValueError("Nonfinite JSON number")

    data = json.loads(
        text, parse_int=Decimal, parse_float=Decimal, parse_constant=invalid
    )
    if not isinstance(data, dict) or not isinstance(data.get("tokens"), list):
        raise ValueError("Expected a tokens array")
    tokens = []
    for token in data["tokens"]:
        if not isinstance(token, dict) or not isinstance(token.get("traits"), list):
            raise ValueError("Expected a token with a traits array")
        traits = []
        for trait in token["traits"]:
            if not isinstance(trait, dict) or "value" not in trait:
                raise ValueError("Expected a trait with a value")
            traits.append(
                TraitInput(
                    trait["trait_type"], trait["value"], trait.get("display_type")
                )
            )
        tokens.append(
            TokenInput(
                token["token_id"], tuple(traits), token.get("token_id_kind", "evm")
            )
        )
    return CollectionInput(tuple(tokens))
