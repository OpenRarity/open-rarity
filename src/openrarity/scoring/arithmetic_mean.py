import numpy as np
from base import BaseRarityFormula
from utils import flatten_attrs, get_attr_probs

from openrarity.models.token import Token


class ArithmeticMeanRarity(BaseRarityFormula):
    """arithmetic mean of a token's n trait probabilities"""

    def score_token(self, token: Token) -> float:
        """calculate the score for a single token"""

        supply = token.collection.token_total_supply
        string_attr_list = flatten_attrs(token.metadata.string_attributes)
        attr_probs = get_attr_probs(string_attr_list, supply)

        return np.mean(attr_probs)
