from dataclasses import dataclass, field
import datetime
from typing import Any

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

    def __init__(self, name: AttributeName, value: float | int):
        # We treat attributes names the same regardless of
        # casing or leading/trailing whitespaces.
        self.name = normalize_attribute_string(name)
        self.value = value


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

    def __init__(self, name: AttributeName, value: int):
        # We treat attributes names the same regardless of
        # casing or leading/trailing whitespaces.
        self.name = normalize_attribute_string(name)
        self.value = value


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


    All attributes names are normalized and all string attribute values are
    normalized in the same way - lowercased and leading/trailing whitespace stripped.
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

    def __post_init__(self):
        self.string_attributes = self._normalize_attributes_dict(
            self.string_attributes
        )
        self.numeric_attributes = self._normalize_attributes_dict(
            self.numeric_attributes
        )
        self.date_attributes = self._normalize_attributes_dict(
            self.date_attributes
        )

    def _normalize_attributes_dict(self, attributes_dict: dict) -> dict:
        """Helper function that takes in an attributes dictionary
        and normalizes attribute name in the dictionary to ensure all
        letters are lower cases and whitespace is stripped.
        """
        normalized_attributes_dict = {}
        for attribute_name, attr in attributes_dict.items():
            normalized_attr_name = normalize_attribute_string(attribute_name)
            normalized_attributes_dict[normalized_attr_name] = attr
            if normalized_attr_name != attr.name:
                attr.name = normalized_attr_name
        return normalized_attributes_dict

    @classmethod
    def from_attributes(cls, attributes: dict[AttributeName, Any]):
        """Constructs TokenMetadata class based on an attributes dictionary

        Parameters
        ----------
        attributes : dict[AttributeName, Any]
            Dictionary of attribute name to attribute value for the given token.
            The type of the value determines whether the attribute is a string,
            numeric or date attribute.

            class           attribute type
            ------------    -------------
            string          string attribute
            int | float     numeric_attribute
            datetime        date_attribute (stored as timestamp, seconds from epoch)

        Returns
        -------
        TokenMetadata
            token metadata from input
        """
        string_attributes = {}
        numeric_attributes = {}
        date_attributes = {}
        for attr_name, attr_value in attributes.items():
            if isinstance(attr_value, str):
                string_attributes[attr_name] = StringAttribute(
                    name=attr_name, value=attr_value
                )
            elif isinstance(attr_value, (float, int)):
                numeric_attributes[attr_name] = NumericAttribute(
                    name=attr_name, value=attr_value
                )
            elif isinstance(attr_value, datetime.datetime):
                date_attributes[attr_name] = DateAttribute(
                    name=attr_name,
                    value=int(attr_value.timestamp()),
                )
            else:
                raise TypeError(
                    f"Provided attribute value has invalid type: {type(attr_value)}. "
                    "Must be either str, float, int or datetime."
                )

        return cls(
            string_attributes=string_attributes,
            numeric_attributes=numeric_attributes,
            date_attributes=date_attributes,
        )
