from openrarity.models.token import Token


def get_attr_probs_weights(
    token: Token, normalized: bool
) -> list[list[float], list[float]]:
    """get attribute probabilities & weights"""

    string_attr_keys = sorted(list(token.metadata.string_attributes.keys()))
    string_attr_list = [
        token.metadata.string_attributes[k] for k in string_attr_keys
    ]
    supply = token.collection.token_total_supply

    if normalized:
        attr_weights = [
            1 / len(token.collection.attributes_count[k])
            for k in string_attr_keys
        ]
    else:
        attr_weights = [1] * len(string_attr_keys)

    return [[attr.count / supply for attr in string_attr_list], attr_weights]
