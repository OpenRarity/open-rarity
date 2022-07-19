import numpy as np
from openrarity.scoring.base import BaseRarityFormula

from openrarity.models.token import Token
from openrarity.scoring.utils import get_attr_probs_weights


class ArithmeticMeanRarity(BaseRarityFormula):
    """arithmetic mean of a token's n trait probabilities"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """Score the token

        Parameters
        ----------
        token : Token
            token
        normalized : bool, optional
            apply traits normalization, True by default
        Returns
        -------
        float
            _description_
        """

        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return np.average(attr_probs, weights=attr_weights)
