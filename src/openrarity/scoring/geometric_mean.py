from dataclasses import dataclass
from models.token import Token
from base import BaseRarityFormula
import numpy as np

@dataclass
class GeometricMeanRarity(BaseRarityFormula):

    formula_name='Geometric Mean Rarity', 
    formula_id=1, 
    description='''
    -- the geometric mean of a token's n trait probabilities
    -- equivalent to the nth root of the product of the trait probabilities
    -- equivalent to the nth power of "statistical rarity"
    '''

    def score_token(self, token: Token) -> float:
        supply = token.collection.token_total_supply

        attr_probs = [attr.count/supply for attr in token.metadata.string_attributes]
        token_prob = np.prod(attr_probs)

        return token_prob**(1/len(token.metadata.string_attributes))