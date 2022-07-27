import numpy as np
from openrarity.scoring.base import BaseRarityFormula

from openrarity.models.token import Token
from openrarity.scoring.utils import get_attr_probs_weights


class SumRarity(BaseRarityFormula):
    """sum of n trait probabilities"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, weights = get_attr_probs_weights(token, normalized)

        return np.dot(attr_probs, weights)
