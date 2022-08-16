from open_rarity.models.collection import Collection, CollectionAttribute
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import (
    StringAttribute,
)

from tests.utils import create_evm_token


class TestCollection:

    attributes = {
        "attribute1": {"value1": 20, "value2": 30},
        "attribute2": {"value1": 10, "value2": 50},
    }
    tokens: list[Token] = [create_evm_token(token_id=i) for i in range(100)]
    test_collection: Collection = Collection(
        name="test",
        tokens=tokens,
        attributes_frequency_counts=attributes,
    )

    test_no_attributes_collection: Collection = Collection(
        name="test2",
        tokens=tokens,
        attributes_frequency_counts={},
    )

    def test_attribute_frequency_counts_initialization(self):
        all_lower_case_attributes = {
            "hat": {"beanie": 40, "cap": 60},
            "bottom": {"special": 1},
        }
        input_attributes_to_expected_output = [
            [all_lower_case_attributes, all_lower_case_attributes],
            # Name and one value has first letter uppercase
            [
                {"Hat": {"beanie": 40, "Cap": 60}, "bottom": {"special": 1}},
                all_lower_case_attributes,
            ],
            # All caps
            [
                {"HAT": {"beanie": 40, "CAP": 60}, "Bottom": {"SPECIAL": 1}},
                all_lower_case_attributes,
            ],
            # Duplicate traits
            [
                {
                    "hat": {"beanie": 40, "cap": 29, "Cap": 31},
                    "bottom": {"special": 1},
                },
                all_lower_case_attributes,
            ],
            # Duplicate trait names
            [
                {
                    "hat": {"beanie": 40, "cap": 25},
                    "Hat": {"Cap": 35},
                    "bottom": {"special": 1},
                },
                all_lower_case_attributes,
            ],
            # Empty
            [{}, {}],
        ]

        for (
            input_attributes,
            expected_attributes,
        ) in input_attributes_to_expected_output:
            c = Collection(
                name="random",
                tokens=[],
                attributes_frequency_counts=input_attributes,
            )
            assert c.attributes_frequency_counts == expected_attributes

    def test_tokens(self):
        collection_1 = Collection(
            name="test",
            tokens=self.tokens,
            attributes_frequency_counts=self.attributes,
        )
        collection_2 = Collection(
            name="test",
            tokens=self.tokens[0:50],
            attributes_frequency_counts={},
        )

        assert collection_1.tokens == self.tokens
        assert collection_2.tokens == self.tokens[0:50]
        assert collection_1.token_total_supply == 100
        assert collection_2.token_total_supply == 50

        new_tokens = [create_evm_token(token_id=100_000)]
        collection_1.tokens = new_tokens
        assert collection_1.tokens == new_tokens
        assert collection_1.token_total_supply == 1

        collection_2.tokens = []
        assert collection_2.tokens == []
        assert collection_2.token_total_supply == 0

    def test_extract_null_attributes(self):
        assert self.test_collection.extract_null_attributes() == {
            "attribute1": CollectionAttribute(
                StringAttribute("attribute1", "Null"), 50
            ),
            "attribute2": CollectionAttribute(
                StringAttribute("attribute2", "Null"), 40
            ),
        }

    def test_extract_null_attributes_empty(self):
        assert (
            self.test_no_attributes_collection.extract_null_attributes() == {}
        )

    def test_extract_collection_attributes(self):
        assert self.test_collection.extract_collection_attributes() == {
            "attribute1": [
                CollectionAttribute(
                    StringAttribute("attribute1", "value1"), 20
                ),
                CollectionAttribute(
                    StringAttribute("attribute1", "value2"), 30
                ),
            ],
            "attribute2": [
                CollectionAttribute(
                    StringAttribute("attribute2", "value1"), 10
                ),
                CollectionAttribute(
                    StringAttribute("attribute2", "value2"), 50
                ),
            ],
        }

    def test_extract_empty_collection_attributes(self):
        assert (
            self.test_no_attributes_collection.extract_collection_attributes()
            == {}
        )
