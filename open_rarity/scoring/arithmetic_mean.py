import logging
import numpy as np
from open_rarity.scoring.base import BaseRarityFormula

from open_rarity.models.token import Token
from open_rarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


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

        logger.debug(
            "Computing arithmetic mean for token {id}".format(
                id=token.token_id
            )
        )

        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return np.average(attr_probs, weights=attr_weights)
