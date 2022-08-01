import logging
import scipy.stats
from open_rarity.scoring.base import BaseRarityFormula

from open_rarity.models.token import Token
from open_rarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class GeometricMeanRarity(BaseRarityFormula):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        logger.debug(
            "Computing geometric mean for token {id}".format(id=token.token_id)
        )

        attr_probs, attr_weights = get_attr_probs_weights(token, normalized)

        return scipy.stats.mstats.gmean(attr_probs, weights=attr_weights)
