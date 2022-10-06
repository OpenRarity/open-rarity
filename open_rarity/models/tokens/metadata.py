from datetime import datetime
from itertools import chain

from pydantic import BaseModel, validator

from open_rarity.models.validators.string import clean_lower_string

from .types import MetadataAttribute


class StringAttribute(BaseModel):
    """Class represents string token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : str
        value of a string attribute
    """

    name: str
    value: str

    string_validation = validator("name", "value", allow_reuse=True)(clean_lower_string)


class NumericAttribute(BaseModel):
    """Class represents numeric token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : float | int
        value of a numeric attribute
    """

    name: str
    value: float | int

    string_validation = validator("name", allow_reuse=True)(clean_lower_string)


class DateAttribute(BaseModel):
    """Class represents date token attribute name and value

    Attributes
    ----------
    name : AttributeName
        name of an attribute
    value : int
        value of a date attribute in UNIX timestamp format
    """

    name: str
    value: datetime

    string_validation = validator("name", allow_reuse=True)(clean_lower_string)


Attribute = StringAttribute | NumericAttribute | DateAttribute


class TokenMetadata(BaseModel):
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

    string_attributes: list[StringAttribute]
    numeric_attributes: list[NumericAttribute]
    date_attributes: list[DateAttribute]

    def parse(cls, metadata: list[MetadataAttribute]):
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
        string_attributes = []
        numeric_attributes = []
        date_attributes = []
        for attr in metadata:
            match attr.default("display_type", None):
                case "string":
                    string_attributes.append(StringAttribute(attr))
                case "number":
                    numeric_attributes.append(NumericAttribute(attr))
                case "date":
                    date_attributes.append(DateAttribute(attr))
                case _:
                    string_attributes.append(StringAttribute(attr))

        return cls(
            string_attributes=string_attributes,
            numeric_attributes=numeric_attributes,
            date_attributes=date_attributes,
        )

    def to_metadata(self) -> list[MetadataAttribute]:
        """Returns a list of dictionaries of all attributes in this metadata object."""
        return list(chain(*self.dict().values()))
