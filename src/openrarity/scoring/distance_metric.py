from models.token import Token
from base import BaseRarityFormula

class DistanceMetricRarity(BaseRarityFormula):
    """the mean number of attribute swaps required to reach another token"""

    def score_token(self, token: Token) -> float:
        # to be implemented
        pass
