import numpy as np
from open_rarity.scoring.scorer import Scorer
from open_rarity.models.collection import Collection
from open_rarity.models.token import Token

from open_rarity.scoring.utils import get_attr_probs_weights


class SumRarityScorer(Scorer):
    """sum of n trait probabilities"""

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        attr_probs, _ = get_attr_probs_weights(collection, token, normalized)
        return np.sum(attr_probs)
