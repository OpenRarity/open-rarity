import numpy as np
from base import BaseRarityFormula
from utils import get_attr_probs

from openrarity.models.token import Token


class GeometricMeanRarity(BaseRarityFormula):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(self, token: Token) -> float:
        """calculate the score for a single token"""

        string_attr_list = list(token.metadata.string_attributes.values())
        attr_probs = get_attr_probs(string_attr_list, token)

        return np.prod(attr_probs) ** (
            1 / len(token.metadata.string_attributes)
        )
