import logging

import numpy as np

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import (
    AttributeName,
    StringAttributeValue,
)
from open_rarity.scoring.scorer import Scorer
from open_rarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class InformationContentRarityScorer(Scorer):
    """Rarity describes the information-theoretic "rarity" of a Collection.
    The concept of "rarity" can be considered as a measure of "surprise" at the
    occurrence of a particular token's properties, within the context of the
    Collection from which it is derived. Self-information is a measure of such
    surprise, and information entropy a measure of the expected value of
    self-information across a distribution (i.e. across a Collection).

    It is trivial to "stuff" a Collection with extra information by merely adding
    additional properties to all tokens. This is reflected in the Entropy field,
    measured in bits—all else held equal, a Collection with more token properties
    will have higher Entropy. However, this information bloat is carried by the
    tokens themselves, so their individual information-content grows in line with
    Collection-wide Entropy. The Scores are therefore scaled down by the Entropy
    to provide unitless "relative surprise", which can be safely compared between
    Collections.

    Rarity computes rarity of each token in the Collection based on information
    entropy. Every TraitType is considered as a categorical probability
    distribution with each TraitValue having an associated probability and hence
    information content. The rarity of a particular token is the sum of
    information content carried by each of its Attributes, divided by the entropy
    of the Collection as a whole (see the Rarity struct for rationale).

    Notably, the lack of a TraitType is considered as a null-Value Attribute as
    the absence across the majority of a Collection implies rarity in those
    tokens that do carry the TraitType.
    """

    # TODO [@danmeshkov]: To support numeric types in a follow-up version.

    def score_token(
        self, collection: Collection, token: Token, normalized: bool = True
    ) -> float:
        return self._score_token(collection, token, normalized)

    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
        normalized: bool = True,
    ) -> list[float]:
        # Memoize for performance
        collection_null_attributes = collection.extract_null_attributes()
        collection_attributes = collection.extract_collection_attributes()
        return [
            self._score_token(
                collection,
                t,
                normalized,
                collection_attributes,
                collection_null_attributes,
            )
            for t in tokens
        ]

    # Private methods
    def _score_token(
        self,
        collection: Collection,
        token: Token,
        normalized: bool = True,
        # If provided, will be used instead of re-calculating on @collection
        collection_attributes: dict[
            AttributeName, list[StringAttributeValue]
        ] = None,
        collection_null_attributes: dict[
            AttributeName, StringAttributeValue
        ] = None,
    ) -> float:
        """calculate the score for a single token"""

        logger.debug(f"Computing InformationContent for token {token}")
        attr_probs, _ = get_attr_probs_weights(
            collection=collection,
            token=token,
            normalized=normalized,
            collection_null_attributes=collection_null_attributes,
        )

        collection_probabilities = self._get_collection_probabilities(
            collection=collection,
            collection_attributes=collection_attributes,
            collection_null_attributes=collection_null_attributes,
        )
        logger.debug(f"Collection_probabilities {collection_probabilities}")

        # Scores are already inverted probabilities. For information content,
        # We need to take sum of logarithms to calculate.
        information_content = -np.sum(np.log2(np.reciprocal(attr_probs)))

        # Now, compute entropy for the whole collection
        collection_entropy = -np.dot(
            collection_probabilities, np.log2(collection_probabilities)
        )

        logger.debug(
            "Information content {probs}".format(probs=information_content)
        )

        logger.debug(
            "Collection {collection} entropy {probs}".format(
                collection=collection.name, probs=collection_entropy
            )
        )

        return information_content / collection_entropy

    def _get_collection_probabilities(
        self,
        collection: Collection,
        collection_attributes: dict[
            AttributeName, list[StringAttributeValue]
        ] = None,
        collection_null_attributes: dict[
            AttributeName, StringAttributeValue
        ] = None,
    ):
        attributes: dict[str, list[StringAttributeValue]] = (
            collection_attributes or collection.extract_collection_attributes()
        )
        null_attributes: dict[str, StringAttributeValue] = (
            collection_null_attributes or collection.extract_null_attributes()
        )

        # collect all probabilities into array
        collection_probabilities = []
        for value, _ in attributes.items():
            null_attr = (
                null_attributes[value] if value in null_attributes else None
            )

            if null_attr:
                attributes[value].append(null_attr)

            collection_probabilities.extend(
                [
                    value.count / collection.token_total_supply
                    for value in attributes[value]
                ]
            )

        return collection_probabilities
