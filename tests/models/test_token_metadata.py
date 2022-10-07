from datetime import datetime

import pytest

from open_rarity.models.token import (
    DateAttribute,
    NumericAttribute,
    StringAttribute,
    TokenMetadata,
)


class TestTokenMetadata:
    def test_from_attributes_valid_types(self):
        created = datetime.now()
        token_metadata = TokenMetadata.from_attributes(
            {
                "hat": "blue cap",
                "created": created,
                "integer trait": 1,
                "float trait": 203.5,
                "PANTS ": "jeans",
            }
        )

        assert token_metadata.string_attributes == {
            "hat": StringAttribute(name="hat", value="blue cap"),
            "pants": StringAttribute(name="pants", value="jeans"),
        }
        assert token_metadata.numeric_attributes == {
            "integer trait": NumericAttribute(name="integer trait", value=1),
            "float trait": NumericAttribute(name="float trait", value=203.5),
        }
        assert token_metadata.date_attributes == {
            "created": DateAttribute(name="created", value=int(created.timestamp())),
        }

    def test_from_attributes_invalid_type(self):
        with pytest.raises(TypeError) as excinfo:
            TokenMetadata.from_attributes(
                {
                    "hat": "blue cap",
                    "created": {"bad input": "true"},
                    "integer trait": 1,
                    "float trait": 203.5,
                }
            )

        assert "Provided attribute value has invalid type" in str(excinfo.value)
