from dataclasses import dataclass
from models.token import Token
from models.collection import Collection

@dataclass
class BaseRarityFormula:
    "base rarity formula"

    formula_name: str
    formula_id: int
    description: str

    def score_token(token: Token) -> float:
        raise NotImplementedError

    # base aggregate scorers: can override w/ more efficient methods

    def score_tokens(self, tokens: list[Token]) -> list[float]:
        return [self.score_token(t) for t in tokens]

    def score_collection(self, collection: Collection) -> list[float]:
        tokens = collection.tokens
        return [self.score_token(t) for t in tokens]

    def score_collections(self, collections: list[Collection]) -> list[list[float]]:
        return [self.score_collection(c) for c in collections]