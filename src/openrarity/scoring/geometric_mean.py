from models.token import Token
from base import BaseRarityFormula
import numpy as np

class GeometricMeanRarity(BaseRarityFormula):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(self, token: Token) -> float:
        """calculate the score for a single token"""

        supply = token.collection.token_total_supply

        # flatten string_attributes dict
        string_attr_list = [x for sublist in token.metadata.string_attributes.items() for x in sublist]

        attr_probs = [attr.count/supply for attr in string_attr_list]

        return np.prod(attr_probs)**(1/len(token.metadata.string_attributes))
