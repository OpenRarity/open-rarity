import logging
import numpy as np
from open_rarity.scoring.base import BaseRarityFormula

from open_rarity.models.token import Token
from open_rarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class HarmonicMeanRarity(BaseRarityFormula):
    """harmonic mean of a token's n trait probabilities"""

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        logger.debug(
            "Computing Harmonic mean for token {id}".format(id=token.token_id)
        )
        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return (
            np.average(np.reciprocal(attr_probs), weights=attr_weights) ** -1
        )
