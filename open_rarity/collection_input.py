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
