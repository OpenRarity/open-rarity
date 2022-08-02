import numpy as np
from open_rarity.scoring.base import BaseRarityFormula

from open_rarity.models.token import Token
from open_rarity.scoring.utils import get_attr_probs_weights


class SumRarity(BaseRarityFormula):
    """sum of n trait probabilities"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, weights = get_attr_probs_weights(token, normalized)

        return np.dot(attr_probs, weights)
