from dataclasses import dataclass, field

AttributeName = str
AttributeValue = str


@dataclass
class StringAttributeValue:
    """Class represents string token attribute name and value

    Attributes
    ----------
    attribute_name : AttributeName
        name of an attribute
    attribute_value : str
        value of a string attribute
    count : int
        total value of tokens in collection that have this attribute
    """

    attribute_name: AttributeName  # duplicate name here for ease of reduce
    attribute_value: str
    count: int


@dataclass
class NumericAttributeValue:
    """Class represents numeric token attribute name and value

    Attributes
    ----------
    attribute_name : AttributeName
        name of an attribute
    attribute_value : float
        value of a string attribute
    count : int
        total value of tokens in collection that have this attribute
    """

    attribute_name: AttributeName
    attribute_value: float


@dataclass
class TokenMetadata:
    """Class represents EIP-721 or EIP-1115 compatible metadata structure

    Attributes
    ----------
    string_attributes : dict
        mapping of atrribute name to list of string attribute values
    numeric_attributes : dict
        mapping of atrribute name to list of numeric attribute values
    """

    string_attributes: dict[AttributeName, StringAttributeValue] = field(
        default_factory=dict
    )
    numeric_attributes: dict[AttributeName, NumericAttributeValue] = field(
        default_factory=dict
    )
