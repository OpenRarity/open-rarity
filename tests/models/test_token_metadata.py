from datetime import datetime

import pytest

from open_rarity.models.token_metadata import (
    DateAttribute,
    NumericAttribute,
    StringAttribute,
    TokenMetadata,
)

now = datetime.now()


class TestTokenMetadata:
    token_metadata = TokenMetadata(
        string_attributes={
            "hat": StringAttribute(name="hat", value="blue cap"),
        },
        numeric_attributes={
            "integer trait": NumericAttribute(name="integer trait", value=1),
        },
        date_attributes={
            "created": DateAttribute(name="created", value=int(now.timestamp())),
        },
    )

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

    def test_attribute_exists(self):
        assert self.token_metadata.attribute_exists("hat")
        assert self.token_metadata.attribute_exists("HAT")
        assert self.token_metadata.attribute_exists("integer trait")
        assert self.token_metadata.attribute_exists("integer trait     ")
        assert self.token_metadata.attribute_exists("created")
        assert not self.token_metadata.attribute_exists("scarf")
        assert not TokenMetadata().attribute_exists("hat")

    def test_add_attribute_empty(self):
        token_metadata = TokenMetadata()
        token_metadata.add_attribute(StringAttribute(name="hat", value="blue cap"))
        token_metadata.add_attribute(NumericAttribute(name="integer trait", value=1))
        token_metadata.add_attribute(
            DateAttribute(name="created", value=int(datetime.now().timestamp()))
        )

        assert token_metadata.string_attributes == {
            "hat": StringAttribute(name="hat", value="blue cap"),
        }
        assert token_metadata.numeric_attributes == {
            "integer trait": NumericAttribute(name="integer trait", value=1),
        }
        assert token_metadata.date_attributes == {
            "created": DateAttribute(
                name="created", value=int(datetime.now().timestamp())
            ),
        }

    def test_add_attribute_non_empty(self):
        created_date = datetime.now()
        token_metadata = TokenMetadata.from_attributes(
            {
                "hat": "blue cap",
                "created": created_date,
                "integer trait": 1,
                "float trait": 203.5,
                "PANTS ": "jeans",
            }
        )
        token_metadata.add_attribute(StringAttribute(name="scarf", value="old"))
        token_metadata.add_attribute(StringAttribute(name="scarf", value="wrap-around"))
        token_metadata.add_attribute(NumericAttribute(name="integer trait 2", value=10))
        created_date_2 = datetime.now()
        token_metadata.add_attribute(
            DateAttribute(name="created 2", value=int(created_date_2.timestamp()))
        )

        assert token_metadata.string_attributes == {
            "hat": StringAttribute(name="hat", value="blue cap"),
            "pants": StringAttribute(name="pants", value="jeans"),
            "scarf": StringAttribute(name="scarf", value="wrap-around"),
        }
        assert token_metadata.numeric_attributes == {
            "integer trait": NumericAttribute(name="integer trait", value=1),
            "float trait": NumericAttribute(name="float trait", value=203.5),
            "integer trait 2": NumericAttribute(name="integer trait 2", value=10),
        }
        assert token_metadata.date_attributes == {
            "created": DateAttribute(
                name="created", value=int(created_date.timestamp())
            ),
            "created 2": DateAttribute(
                name="created 2", value=int(created_date_2.timestamp())
            ),
        }

    def test_metadata_to_attributes(self):
        attribute_dict = self.token_metadata.to_attributes()

        assert attribute_dict["hat"] == "blue cap"
        assert attribute_dict["integer trait"] == 1

        # the microseconds will get lost so compare to a datetime without them
        assert attribute_dict["created"] == datetime(
            now.year, now.month, now.day, now.hour, now.minute, now.second
        )
