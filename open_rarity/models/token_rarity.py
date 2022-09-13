from dataclasses import dataclass

from open_rarity.models.token import Token


@dataclass
class TokenRarity:
    """The class holds rarity and optional rank information along with the token

    Attributes
    ----------
    score : float
        OpenRarity score for the token within collection
    token : Token
        token class
    rank: int | None
        rank of the token within the collection
    """

    score: float
    token: Token
    rank: int | None = None
