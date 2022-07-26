import logging
import numpy as np
from openrarity.models.collection import Collection
from openrarity.models.token import Token
from openrarity.models.token_metadata import StringAttributeValue
from openrarity.scoring.base import BaseRarityFormula
from openrarity.scoring.utils import get_attr_probs_weights

logger = logging.getLogger("open_rarity_logger")


class InformationContentRarity(BaseRarityFormula):
    """Computes rarity of each token
    based on the idea of entropy and information content"""

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
        information_content = -sum(np.log2(np.reciprocal(scores)))

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
