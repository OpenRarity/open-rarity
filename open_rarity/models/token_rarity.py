from dataclasses import dataclass


@dataclass
class TokenRarity:
    """The class holds rarity and rank information for the token in Collection"""

    score: float
    rank: int | None = None
