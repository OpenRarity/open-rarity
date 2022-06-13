from dataclasses import dataclass

AttributeName = str


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
    custom_values : dict[str,str]
        dict of additional metadata related to attributes,
    """

    attribute_name: AttributeName  # duplicate name here for ease of reduce
    attribute_value: str
    count: int
    custom_values: dict[str, str]


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
    custom_values : dict[str,str]
        dict of additional metadata related to attributes,
    """

    attribute_name: AttributeName
    attribute_value: float
    custom_values: dict[str, str]


StringAttributeValuesList = list[StringAttributeValue]
NumericAttributeValuesList = list[NumericAttributeValue]


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

    string_attributes: dict[AttributeName, StringAttributeValuesList]
    numeric_attributes: dict[AttributeName, NumericAttributeValuesList]
