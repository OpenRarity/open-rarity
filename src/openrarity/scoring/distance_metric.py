from dataclasses import dataclass
from models.token import Token
from base import BaseRarityFormula
import numpy as np

@dataclass
class DistanceMetricRarity(BaseRarityFormula):

    formula_name='Distance Metric Rarity', 
    formula_id=1, 
    description='''
    -- the mean number of attribute swaps required to reach another token
    '''

    def score_token(self, token: Token) -> float:
        # to be implemented
        pass