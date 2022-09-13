import logging

import numpy as np

from open_rarity.models.collection import Collection, CollectionAttribute
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import AttributeName
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights

logger = logging.getLogger("open_rarity_logger")


class InformationContentScoringHandler:
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

    This class computes rarity of each token in the Collection based on information
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

    def score_token(self, collection: Collection, token: Token) -> float:
        """See ScoringHandler interface.

        Limitations
        -----------
            Does not take into account non-String attributes during scoring.

        """
        return self._score_token(collection, token)

    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
    ) -> list[float]:
        """See ScoringHandler interface.

        Limitations
        -----------
            Does not take into account non-String attributes during scoring.

        """
        # Precompute for performance
        collection_null_attributes = collection.extract_null_attributes()
        collection_attributes = collection.extract_collection_attributes()
        collection_entropy = self._get_collection_entropy(
            collection=collection,
            collection_attributes=collection_attributes,
            collection_null_attributes=collection_null_attributes,
        )
        return [
            self._score_token(
                collection=collection,
                token=t,
                collection_null_attributes=collection_null_attributes,
                # covering the corner case when collection has one item.
                collection_entropy_normalization=collection_entropy
                if collection_entropy
                else 1,
            )
            for t in tokens
        ]

    # Private methods
    def _score_token(
        self,
        collection: Collection,
        token: Token,
        collection_null_attributes: dict[
            AttributeName, CollectionAttribute
        ] = None,
        collection_entropy_normalization: float = None,
    ) -> float:
        """Calculates the score of the token using information entropy with a
        collection entropy normalization factor.

        Parameters
        ----------
        collection : Collection
            The collection with the attributes frequency counts to base the
            token trait probabilities on to calculate score.
        token : Token
            The token to score
        collection_null_attributes : dict[AttributeName, CollectionAttribute], optional
            Optional memoization of collection.extract_null_attributes(),
            by default None.
        collection_entropy_normalization : float, optional
            Optional memoization of the collection entropy normalization factor,
            by default None.

        Returns
        -------
        float
            The token score
        """
        logger.debug("Computing score for token %s", token)

        # First calculate the individual attribute scores for all attributes
        # of the provided token. Scores are the inverted probabilities of the
        # attribute in the collection.
        attr_scores, _ = get_token_attributes_scores_and_weights(
            collection=collection,
            token=token,
            normalized=False,
            collection_null_attributes=collection_null_attributes,
        )

        # Get a single score (via information content) for the token by taking
        # the sum of the logarithms of the attributes' scores.
        ic_token_score = -np.sum(np.log2(np.reciprocal(attr_scores)))
        logger.debug("IC token score %s", ic_token_score)

        # Now, calculate the collection entropy to use as a normalization for
        # the token score if its not provided
        if collection_entropy_normalization is None:
            collection_entropy = self._get_collection_entropy(
                collection=collection,
                collection_attributes=collection.extract_collection_attributes(),
                collection_null_attributes=collection_null_attributes,
            )
        else:
            collection_entropy = collection_entropy_normalization
        normalized_token_score = ic_token_score / collection_entropy
        logger.debug(
            "Finished scoring %s %s: collection entropy: %s token scores: %s",
            collection,
            token,
            collection_entropy,
            normalized_token_score,
        )

        return normalized_token_score

    def _get_collection_entropy(
        self,
        collection: Collection,
        collection_attributes: dict[
            AttributeName, list[CollectionAttribute]
        ] = None,
        collection_null_attributes: dict[
            AttributeName, CollectionAttribute
        ] = None,
    ) -> float:
        """Calculates the entropy of the collection, defined to be the
        sum of the probability of every possible attribute name/value pair that
        occurs in the collection times that square root of such probability.

        Parameters
        ----------
        collection : Collection
            The collection to calculate probability on
        collection_attributes : dict[AttributeName, list[CollectionAttribute]], optional
            Optional memoization of collection.extract_collection_attributes(),
            by default None.
        collection_null_attributes : dict[AttributeName, CollectionAttribute], optional
            Optional memoization of collection.extract_null_attributes(),
            by default None.

        Returns
        -------
        float
            the collection entropy

        Limitations
        -----------
            Does not take into account non-String attributes during scoring.
        """
        attributes: dict[str, list[CollectionAttribute]] = (
            collection_attributes or collection.extract_collection_attributes()
        )
        null_attributes: dict[str, CollectionAttribute] = (
            collection_null_attributes or collection.extract_null_attributes()
        )

        # Create a list of all probabilities for every attribute name/value pair,
        # in the order of collection.attributes_frequency_counts.items()
        collection_probabilities: list[float] = []
        for attr_name, attr_values in attributes.items():
            if attr_name in null_attributes:
                null_attr = null_attributes[attr_name]
                attr_values.append(null_attr)

            # Create an array of the probability of all possible attr_name/value combos
            # existing in the collection
            collection_probabilities.extend(
                [
                    attr_value.total_tokens / collection.token_total_supply
                    for attr_value in attr_values
                ]
            )

        logger.debug(
            "Calculated collection probabilties: %s", collection_probabilities
        )
        collection_entropy = -np.dot(
            collection_probabilities, np.log2(collection_probabilities)
        )

        return collection_entropy
