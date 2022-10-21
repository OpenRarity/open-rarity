from logging import Logger
from typing import Literal

from pydantic import BaseModel, root_validator, validator

from openrarity.validators.string import clean_lower_string

logger = Logger(__name__)


class MetadataAttributeModel(BaseModel):
    """ """

    name: str
    value: float | int | str
    display_type: None | Literal["string", "number", "date"] = "string"

    name_validator = validator("name", allow_reuse=True)(clean_lower_string)

    @root_validator(pre=True)
    def clean_attribute_value(cls, values):
        if "trait_type" in values:
            values["name"] = values.pop("trait_type")
        dtype = values["display_type"]
        value = values["value"]
        if dtype in ["number", "date"]:
            logger.warn(
                f"'{dtype}' are not supported and will not be considered when ranking."
            )
        if isinstance(value, str):
            values["value"] = clean_lower_string(value)
        return values
