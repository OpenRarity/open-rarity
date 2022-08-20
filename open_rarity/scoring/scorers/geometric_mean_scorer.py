import logging

import scipy.stats

from open_rarity.models.collection import Collection, CollectionAttribute
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import AttributeName
from open_rarity.scoring.scorer import Scorer
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights

logger = logging.getLogger("open_rarity_logger")


class GeometricMeanRarityScorer(Scorer):
    """geometric mean of a token's n trait probabilities
    - equivalent to the nth root of the product of the trait probabilities
    - equivalent to the nth power of "statistical rarity"
    """

    def score_token(
        self, collection: Collection, token: Token, normalized: bool = True
    ) -> float:
        super().score_token(collection, token, normalized)
        return self._score_token(collection, token, normalized)

    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
        normalized: bool = True,
    ) -> list[float]:
        super().score_tokens(collection, tokens, normalized)
        collection_null_attributes = collection.extract_null_attributes()
        return [
            self._score_token(
                collection, t, normalized, collection_null_attributes
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
        """Calculates the score of the token by taking the geometric mean of the
        attribute scores with weights.

        Args:
            collection (Collection): The collection with the attributes frequency
                counts to base the token trait probabilities on.
            token (Token): The token to score
            normalized (bool, optional):
                Set to true to enable individual trait normalizations based on
                total number of possible values for an attribute.
                Defaults to True.
            collection_null_attributes
                (dict[ AttributeName, CollectionAttribute ], optional):
                Optional memoization of collection.extract_null_attributes().
                Defaults to None.

        Returns:
            float: The token score
        """
        logger.debug(
            f"Computing geometric mean for {collection} token {token}"
        )

        attr_scores, attr_weights = get_token_attributes_scores_and_weights(
            collection=collection,
            token=token,
            normalized=normalized,
            collection_null_attributes=collection_null_attributes,
        )

        return scipy.stats.mstats.gmean(attr_scores, weights=attr_weights)
