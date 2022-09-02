import logging

import numpy as np

from open_rarity.models.collection import Collection, CollectionAttribute
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import AttributeName
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights

logger = logging.getLogger("open_rarity_logger")


class ArithmeticMeanScoringHandler:
    """arithmetic mean of a token's n trait probabilities"""

    def __init__(self, normalized: bool = True):
        """
        Parameters
        ----------
        normalized : bool, optional
            If true, individual traits will be normalized based on total number
            of possible values for an attribute name, by default True.
        """
        self.normalized = normalized

    def score_token(self, collection: Collection, token: Token) -> float:
        return self._score_token(collection, token, self.normalized)

    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
    ) -> list[float]:
        collection_null_attributes = collection.extract_null_attributes()
        return [
            self._score_token(
                collection, t, self.normalized, collection_null_attributes
            )
            for t in tokens
        ]

    # Private methods
    def _score_token(
        self,
        collection: Collection,
        token: Token,
        normalized: bool = True,
        collection_null_attributes: dict[
            AttributeName, CollectionAttribute
        ] = None,
    ) -> float:
        """Calculates the score of the token by taking the arithmetic mean of
        the attribute scores with weights.

        Parameters
        ----------
        collection : Collection
            The collection with the attributes frequency counts to base the token
            trait probabilities on.
        token : Token
            The token to score.
        normalized : bool, optional
            Set to true to enable individual trait normalizations based on total
            number of possible values for an attribute, by default True.
        collection_null_attributes : dict[AttributeName, CollectionAttribute], optional
            Optional memoization of collection.extract_null_attributes(), by
            default None

        Returns
        -------
        float
            The token score
        """
        logger.debug("Computing arithmetic mean for token %s", token)

        attr_scores, attr_weights = get_token_attributes_scores_and_weights(
            collection=collection,
            token=token,
            normalized=normalized,
            collection_null_attributes=collection_null_attributes,
        )

        logger.debug(
            "[amean] Calculated for %s %s:%s %s",
            collection,
            token,
            attr_scores,
            attr_weights,
        )

        avg = float(np.average(attr_scores, weights=attr_weights))
        return avg
