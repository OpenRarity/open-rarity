import logging
import numpy as np

from openrarity.scoring.scorer import Scorer

from openrarity.models.token import Token
from openrarity.models.collection import Collection
from openrarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class HarmonicMeanRarityScorer(Scorer):
    """harmonic mean of a token's n trait probabilities"""

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token based on the collection's trait distribution"""

        logger.debug(f"Computing Harmonic mean for token {token}")
        attr_probs, attr_weights = get_attr_probs_weights(collection, token, normalized)

        return float(
            np.average(np.reciprocal(attr_probs), weights=attr_weights) ** -1
        )
