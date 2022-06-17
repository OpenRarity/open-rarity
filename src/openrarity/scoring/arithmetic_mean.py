from models.token import Token
from base import BaseRarityFormula
import numpy as np

class ArithmeticMeanRarity(BaseRarityFormula):
    """arithmetic mean of a token's n trait probabilities"""

    def score_token(self, token: Token) -> float:
        """calculate the score for a single token"""

        supply = token.collection.token_total_supply

        # flatten string_attributes dict
        string_attr_list = [x for sublist in token.metadata.string_attributes.items() for x in sublist]

        attr_probs = [attr.count/supply for attr in string_attr_list]
        
        return np.mean(attr_probs)
