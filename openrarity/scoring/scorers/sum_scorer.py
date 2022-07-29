import numpy as np
from openrarity.scoring.scorer import Scorer
from openrarity.models.collection import Collection
from openrarity.models.token import Token

from openrarity.scoring.utils import get_attr_probs_weights


class SumRarityScorer(Scorer):
    """sum of n trait probabilities"""

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, _ = get_attr_probs_weights(collection, token, normalized)
        return np.sum(attr_probs)
