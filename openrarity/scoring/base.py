from openrarity.models.collection import Collection
from openrarity.models.token import Token


class BaseRarityFormula:
    """base rarity class"""

    def score_token(self, token: Token, normalized: bool) -> float:
        raise NotImplementedError

    # base aggregate scorers: can override w/ more efficient methods

    def score_tokens(
        self, tokens: list[Token], normalized: bool
    ) -> list[float]:
        return [self.score_token(t) for t in tokens]

    def score_collection(
        self, collection: Collection, normalized: bool
    ) -> list[float]:
        tokens = collection.tokens
        return [self.score_token(t) for t in tokens]

    def score_collections(
        self, collections: list[Collection], normalized: bool
    ) -> list[list[float]]:
        return [self.score_collection(c) for c in collections]
