from openrarity.models.token import Token
from openrarity.models.token_metadata import StringAttributeValue


def flatten_attrs(
    string_attr_metadata_dict: dict[str, list[StringAttributeValue]]
) -> list[StringAttributeValue]:
    """flatten string_attributes dict"""

    return [
        x for sublist in string_attr_metadata_dict.values() for x in sublist
    ]


def get_attr_probs(
    string_attr_list: list[StringAttributeValue], token: Token
) -> list[float]:
    """get list of attribute probabilities"""

    supply = token.collection.token_total_supply
    return [attr.count / supply for attr in string_attr_list]
