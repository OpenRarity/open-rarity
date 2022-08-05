import logging

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import AttributeName, StringAttributeValue

logger = logging.getLogger("open_rarity_logger")


def get_attr_probs_weights(
    collection: Collection,
    token: Token,
    normalized: bool,
    collection_null_attributes: dict[AttributeName, StringAttributeValue] = None,
) -> tuple[list[float], list[float]]:
    """get attribute probabilities & weights"""
    logger.debug(f"> Collection {collection} Token {token} evaluation")

    logger.debug(f"Attributes array with null-traits {null_attributes}")
    null_attributes = collection_null_attributes or collection.extract_null_attributes()

    # Here we augment the attributes array with probabilities of the attributes with
    # Null attributes consider the probability of that trait not in set.

    logger.debug(f"Attributes array {combined_attributes}")

    string_attr_keys = sorted(list(combined_attributes.keys()))
    string_attr_list = [combined_attributes[k] for k in string_attr_keys]

    logger.debug(
        "Asset attributes dict {attrs}".format(attrs=string_attr_list)
    )

    supply = collection.token_total_supply
    logger.debug(f"Collection supply {supply}")

    # Normalize traits weight by applying  1/x function for each
    # respective trait of the token.
    # The normalization factor takes into account the cardinality
    # values for particual trait.
    # Example: if Asset has a trait "Hat" and it has possible values
    # {"Red","Yellow","Green"} the normalization factor will be 1/3 or
    # 0.33.
    if normalized:
        logger.debug(
            "Attribute count {attr_count}".format(
                attr_count=collection.attributes_distribution
            )
        )

        attr_weights = [1 / len(collection.attributes_frequency_counts[k]) for k in string_attr_keys]
    else:
        attr_weights = [1.0] * len(string_attr_keys)

    scores = [supply / attr.count for attr in string_attr_list]

    logger.debug("Weights {attr_weights}".format(attr_weights=attr_weights))
    logger.debug("Scores {scores}".format(scores=scores))

    return (scores, attr_weights)
