import logging
import numpy as np
from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import StringAttributeValue
from open_rarity.scoring.base import BaseRarityFormula
from open_rarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class InformationContentRarity(BaseRarityFormula):
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

    def score_token(self, token: Token, normalized: bool = True) -> float:
        """calculate the score for a single token"""

        logger.debug(
            "Computing InformationContent for token {id}".format(
                id=token.token_id
            )
        )
        # Scores are already inverted probabilities ,
        # We need to take sum of logarithms to estimate
        # information content.
        scores, _ = get_attr_probs_weights(token, normalized)

        collection_probabilities = self.get_collection_probabilities(
            collection=token.collection
        )
        logger.debug(
            "Collection_probabilities {probs}".format(
                probs=collection_probabilities,
            )
        )

        # Scores are already inverted probabilities ,
        # We need to take sum of logarithms to estimate
        # information content.
        information_content = -np.sum(np.log2(np.reciprocal(scores)))

        # compute entropy for the whole collection
        collection_entropy = -np.dot(
            collection_probabilities, np.log2(collection_probabilities)
        )

        logger.debug(
            "Information content {probs}".format(probs=information_content)
        )

        logger.debug(
            "Collection {collection} entropy {probs}".format(
                collection=token.collection.name, probs=collection_entropy
            )
        )

        return information_content / collection_entropy

    def get_collection_probabilities(self, collection: Collection):
        collection_attributes: dict[
            str, list[StringAttributeValue]
        ] = collection.extract_collection_attributes()
        collection_null_attributes: dict[
            str, StringAttributeValue
        ] = collection.extract_null_attributes

        # collect all probabilities into array
        collection_probabilities = []
        for value, _ in collection_attributes.items():
            null_attr = (
                collection_null_attributes[value]
                if value in collection_null_attributes
                else None
            )

            if null_attr:
                collection_attributes[value].append(null_attr)

            collection_probabilities.extend(
                [
                    value.count / collection.token_total_supply
                    for value in collection_attributes[value]
                ]
            )

        return collection_probabilities
