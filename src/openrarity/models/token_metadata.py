from dataclasses import dataclass

AttirbuteName = str
StringAttirbuteValue = str
NumericAttirbuteValue = float


@dataclass
class StringAttributeValue:
    """Class represents string token attribute name and value

    Attributes:
        attribute_name (AttirbuteName): name of an attribute
        attribute_value (StringAttirbuteValue): value of a string attribute
        count (int): total value of tokens in collection
                     that have this attribute
        custom_values: dict of additional metadata related to attributes,
    """

    attribute_name: AttirbuteName  # duplicate name here for ease of reduce
    atribute_value: StringAttirbuteValue
    count: int
    custom_values: dict[str, str]


@dataclass
class NumericAttributeValue:
    """Class represents numeric token attribute name and value

    Attributes:
        attribute_name (AttirbuteName): name of an attribute
        attribute_value (NumericAttirbuteValue): value of a string attribute
        count (int): total value of tokens in collection
                     that have this attribute
        custom_values (dict[str,str]): dict of additional
                     metadata related to attributes,
    """

    attribute_name: AttirbuteName
    atribute_value: NumericAttirbuteValue
    custom_values: dict[str, str]


StringAttributeValuesList = list[StringAttributeValue]
NumericAttributeValuesList = list[NumericAttributeValue]


@dataclass
class TokenMetadata:
    """Class represents EIP-721 or EIP-1115 compatible metadata structure

    Attributes:
        string_attributes (dict): mapping of atrribute name
                                  to list of string attribute values
        numeric_attributes (dict): mapping of atrribute name
                                  to list of numeric attribute values
    """

    string_attributes: dict[AttirbuteName, list[StringAttributeValue]]
    numeric_attributes: dict[AttirbuteName, list[NumericAttributeValue]]
