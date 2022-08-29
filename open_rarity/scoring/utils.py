from open_rarity.models.collection import Collection, CollectionAttribute
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import AttributeName


def get_token_attributes_scores_and_weights(
    collection: Collection,
    token: Token,
    normalized: bool,
    collection_null_attributes: dict[
        AttributeName, CollectionAttribute
    ] = None,
) -> tuple[list[float], list[float]]:
    """Calculates the scores and normalization weights for a token
    based on its attributes. If the token does not have an attribute, the probability
    of the attribute being null is used instead.

    Parameters
    ----------
    collection : Collection
        The collection to calculate probability on.
    token : Token
        The token to score.
    normalized : bool
        Set to true to enable individual trait normalizations based on total
        number of possible values for an attribute, by default True.
    collection_null_attributes : dict[ AttributeName, CollectionAttribute ], optional
        Optional memoization of collection.extract_null_attributes(), by default None.

    Returns
    -------
    tuple[list[float], list[float]]
        A tuple of attribute scores and attribute weights.
        attribute scores: scores for an attribute is defined to be the inverse of
            the probability of that attribute existing across the collection. e.g.
            (total token supply / total tokens with that attribute name and value)
        attribute weights: The weights for each score that should be applied
            if normalization is to occur.
    """
    # Create a combined attributes dictionary such that if the token has the attribute,
    # it uses the value's probability, and if it doesn't have the attribute,
    # uses the probability of that attribute being null.
    if collection_null_attributes is None:
        null_attributes = collection.extract_null_attributes()
    else:
        null_attributes = collection_null_attributes

    combined_attributes: dict[
        str, CollectionAttribute
    ] = null_attributes | _convert_to_collection_attributes_dict(
        collection, token
    )

    sorted_attr_names = sorted(list(combined_attributes.keys()))
    sorted_attrs = [
        combined_attributes[attr_name] for attr_name in sorted_attr_names
    ]

    total_supply = collection.token_total_supply

    # Normalize traits by dividing by the total number of possible values for
    # that trait. The normalization factor takes into account the cardinality
    # values for particual traits, such that high cardinality traits aren't
    # over-indexed in rarity.
    # Example: If Asset has a trait "Hat" and it has possible values
    # {"Red","Yellow","Green"} the normalization factor will be 1/3 or
    # 0.33. If a trait has 10,000 options, than the normalization factor is 1/10,000.
    if normalized:
        attr_weights = [
            1 / collection.total_attribute_values(attr_name)
            for attr_name in sorted_attr_names
        ]
    else:
        attr_weights = [1.0] * len(sorted_attr_names)

    scores = [total_supply / attr.total_tokens for attr in sorted_attrs]

    return (scores, attr_weights)


def _convert_to_collection_attributes_dict(collection, token):
    # NOTE: We currently only support string attributes
    return {
        attribute.name: CollectionAttribute(
            attribute=attribute,
            total_tokens=collection.total_tokens_with_attribute(attribute),
        )
        for attribute in token.metadata.string_attributes.values()
    }
