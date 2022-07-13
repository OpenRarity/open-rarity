import numpy as np
from openrarity.scoring.base import BaseRarityFormula

from openrarity.models.token import Token
from openrarity.scoring.utils import get_attr_probs_weights


class HarmonicMeanRarity(BaseRarityFormula):
    """harmonic mean of a token's n trait probabilities"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return (
            np.average(np.reciprocal(attr_probs), weights=attr_weights) ** -1
        )
