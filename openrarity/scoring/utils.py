import logging

from openrarity.models.token import Token
from openrarity.models.token_metadata import StringAttributeValue

logger = logging.getLogger("open_rarity_logger")


def get_attr_probs_weights(
    token: Token, normalized: bool
) -> tuple[list[float], list[float]]:
    """get attribute probabilities & weights"""

    logger.debug(
        "> Collection {collection} Token {id} evaluation".format(
            id=token.token_id, collection=token.collection.name
        )
    )

    logger.debug(
        "Attributes array with null-traits {attrs}".format(
            attrs=token.collection.extract_null_attributes
        )
    )

    # Here we augment the attributes array with probabilities of the attributes with
    # Null attributes consider the probability of that trait not in set.
    combined_attributes: dict[str, StringAttributeValue] = (
        token.collection.extract_null_attributes
        | token.metadata.string_attributes
    )

    logger.debug("Attributes array {attr}".format(attr=combined_attributes))

    string_attr_keys = sorted(list(combined_attributes.keys()))
    string_attr_list = [combined_attributes[k] for k in string_attr_keys]

    logger.debug(
        "Asset attributes dict {attrs}".format(attrs=string_attr_list)
    )

    supply = token.collection.token_total_supply

    logger.debug("Collection supply {supl}".format(supl=supply))

    # normalize traits weight by applying  1/x function for each
    # respective trait of the token.
    # The normalization factor takes into account the cardinality
    # values for particual trait.
    # Example: if Asset has a trait "Hat" and it has possible values
    # {"Red","Yellow","Green"} the normalization factor will be 1/3 or
    # 0.33.
    if normalized:
        logger.debug(
            "Attribute count {attr_count}".format(
                attr_count=token.collection.attributes_count
            )
        )

        attr_weights = [
            1 / len(token.collection.attributes_count[k])
            for k in string_attr_keys
        ]
    else:
        attr_weights = [1.0] * len(string_attr_keys)

    scores = [supply / attr.count for attr in string_attr_list]

    logger.debug("Weights {attr_weights}".format(attr_weights=attr_weights))
    logger.debug("Scores {scores}".format(scores=scores))

    return (scores, attr_weights)
