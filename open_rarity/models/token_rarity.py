from dataclasses import dataclass

from open_rarity.models.token import Token
from open_rarity.models.token_ranking_features import TokenRankingFeatures


@dataclass
class TokenRarity:
    """The class holds rarity and optional rank information along with the token

    Attributes
    ----------
    score : float
        OpenRarity score for the token within collection
    token : Token
        token class
    token_features : TokenFeatures
        various token features
    rank: int | None
        rank of the token within the collection
    """

    score: float
    token_features: TokenRankingFeatures
    token: Token
    rank: int | None = None
