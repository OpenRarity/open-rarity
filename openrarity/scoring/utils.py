import logging

from openrarity.models.token import Token

logger = logging.getLogger("testset_resolver")


def get_attr_probs_weights(
    token: Token, normalized: bool
) -> tuple[list[float], list[float]]:
    """get attribute probabilities & weights"""

    logger.debug(
        "> Collection {collection} Token {id} evaluation".format(
            id=token.token_id, collection=token.collection.name
        )
    )

    string_attr_keys = sorted(list(token.metadata.string_attributes.keys()))

    string_attr_list = [
        token.metadata.string_attributes[k] for k in string_attr_keys
    ]

    logger.debug(
        "Asset attributes dict {attrs}".format(attrs=string_attr_list)
    )

    supply = token.collection.token_total_supply

    logger.debug("Collection supply {supl}".format(supl=supply))

    # normalize traits weight by applying  1/x function for each
    # respective trait of the token
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
