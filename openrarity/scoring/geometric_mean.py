import scipy.stats
from openrarity.scoring.base import BaseRarityFormula

from openrarity.models.token import Token
from openrarity.scoring.utils import get_attr_probs_weights


class GeometricMeanRarity(BaseRarityFormula):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return scipy.stats.mstats.gmean(attr_probs, weights=attr_weights)
