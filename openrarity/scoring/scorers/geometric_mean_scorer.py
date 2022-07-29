import logging
import scipy.stats
from openrarity.scoring.scorer import Scorer

from openrarity.models.token import Token
from openrarity.models.collection import Collection
from openrarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class GeometricMeanRarityScorer(Scorer):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""
        logger.debug(f"Computing geometric mean for {collection} token {token}")

        attr_probs, attr_weights = get_attr_probs_weights(collection, token, normalized)
        return scipy.stats.mstats.gmean(attr_probs, weights=attr_weights)
