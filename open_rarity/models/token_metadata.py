from dataclasses import dataclass, field

from open_rarity.models.utils.attribute_utils import normalize_attribute_string

AttributeName = str
AttributeValue = str


@dataclass
class StringAttribute:
    """Class represents string token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : str
        value of a string attribute
    """

    name: AttributeName  # duplicate name here for ease of reduce
    value: AttributeValue

    def __init__(self, name: AttributeName, value: AttributeValue):
        # We treat string attributes name and value the same regardless of
        # casing or leading/trailing whitespaces.
        self.name = normalize_attribute_string(name)
        self.value = normalize_attribute_string(value)


@dataclass
class NumericAttribute:
    """Class represents numeric token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : float | int
        value of a numeric attribute
    """

    name: AttributeName
    value: float | int


@dataclass
class DateAttribute:
    """Class represents date token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : int
        value of a date attribute in UNIX timestamp format
    """

    name: AttributeName
    value: int


@dataclass
class TokenMetadata:
    """Class represents EIP-721 or EIP-1115 compatible metadata structure

    Attributes
    ----------
    string_attributes : dict
        mapping of atrribute name to list of string attribute values
    numeric_attributes : dict
        mapping of atrribute name to list of numeric attribute values
    date_attributes : dict
        mapping of attribute name to list of date attribute values
    """

    string_attributes: dict[AttributeName, StringAttribute] = field(
        default_factory=dict
    )
    numeric_attributes: dict[AttributeName, NumericAttribute] = field(
        default_factory=dict
    )
    date_attributes: dict[AttributeName, DateAttribute] = field(
        default_factory=dict
    )
