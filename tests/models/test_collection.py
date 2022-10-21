from openrarity.collection.collection import Collection, CollectionAttribute
from openrarity.token.metadata import StringAttribute, TokenMetadata
from openrarity.token.standard import TokenStandard
from openrarity.token.token import Token
from tests.helpers import (
    create_evm_token,
    create_numeric_evm_token,
    generate_mixed_collection,
)


class TestCollection:

    attributes = {
        "attribute1": {"value1": 20, "value2": 30},
        "attribute2": {"value1": 10, "value2": 50},
    }
    tokens: list[Token] = [create_evm_token(token_id=i) for i in range(100)]

    string_numeric_tokens: list[Token] = [
        create_evm_token(token_id=i) for i in range(50)
    ] + [create_numeric_evm_token(token_id=i) for i in range(50, 100)]

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

    test_numeric_attributes_collection: Collection = Collection(
        name="test3",
        tokens=string_numeric_tokens,
        attributes_frequency_counts=attributes,
    )

    test_mixed_erc_collection: Collection = Collection(
        name="test4",
        tokens=[create_evm_token(token_id=i) for i in range(10)]
        + [
            create_evm_token(token_id=i, token_standard=TokenStandard.ERC1155)
            for i in range(10, 50)
        ]
        + [create_evm_token(token_id=i) for i in range(50, 60)],
        attributes_frequency_counts={},
    )

    test_erc1155_collection: Collection = Collection(
        name="test4",
        tokens=[
            create_evm_token(token_id=i, token_standard=TokenStandard.ERC1155)
            for i in range(10)
        ],
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
            # Trailing or leading whitespaces
            [
                {
                    " hat": {"beanie": 40, "cap": 25},
                    "Hat ": {"Cap": 35},
                    "bottom": {"special": 1},
                },
                all_lower_case_attributes,
            ],
            # Middle whitespace
            [
                {
                    "hat": {
                        "big beanie": 40,
                        "cap": 25,
                        "big beanie ": 10,
                        "beanie": 5,
                    },
                },
                {"hat": {"big beanie": 50, "cap": 25, "beanie": 5}},
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
        assert self.test_no_attributes_collection.extract_null_attributes() == {}

    def test_extract_collection_attributes(self):
        assert self.test_collection.extract_collection_attributes() == {
            "attribute1": [
                CollectionAttribute(StringAttribute("attribute1", "value1"), 20),
                CollectionAttribute(StringAttribute("attribute1", "value2"), 30),
            ],
            "attribute2": [
                CollectionAttribute(StringAttribute("attribute2", "value1"), 10),
                CollectionAttribute(StringAttribute("attribute2", "value2"), 50),
            ],
        }

    def test_extract_empty_collection_attributes(self):
        assert self.test_no_attributes_collection.extract_collection_attributes() == {}

    def test_has_numeric_attributes(self):
        assert self.test_numeric_attributes_collection.has_numeric_attribute
        assert not self.test_collection.has_numeric_attribute

    def test_collection_without_attributes_init(self):
        collection = Collection(
            tokens=[
                create_evm_token(
                    token_id=1,
                    metadata=TokenMetadata.parse(
                        {
                            "hat": "cap",
                            "bottom": "jeans",
                            "something another": "special",
                        }
                    ),
                ),
                create_evm_token(
                    token_id=2,
                    metadata=TokenMetadata.parse(
                        {
                            "hat": "cap",
                            "bottom": "pjs",
                            "something another": "not special",
                        }
                    ),
                ),
                create_evm_token(
                    token_id=2,
                    metadata=TokenMetadata.parse(
                        {
                            "hat": "bucket hat",
                            "new": "very special",
                            "integer trait - will not be shown": 1,
                        }
                    ),
                ),
            ]
        )

        assert collection.attributes_frequency_counts == {
            "hat": {
                "cap": 2,
                "bucket hat": 1,
            },
            "bottom": {
                "jeans": 1,
                "pjs": 1,
            },
            "something another": {"special": 1, "not special": 1},
            "new": {"very special": 1},
        }

    def test_collection_without_attributes_init_equality(self):
        large_collection = generate_mixed_collection()
        comparable_collection = Collection(tokens=large_collection.tokens)
        assert (
            comparable_collection.attributes_frequency_counts
            == large_collection.attributes_frequency_counts
        )

    def test_token_standards(self):
        assert self.test_collection.tokens.standards == [TokenStandard.ERC721]
        assert self.test_no_attributes_collection.tokens.standards == [
            TokenStandard.ERC721
        ]
        assert self.test_erc1155_collection.tokens.standards == [TokenStandard.ERC1155]

        # Test mixed collection
        mixed_standards = self.test_mixed_erc_collection.tokens.standards
        assert len(mixed_standards) == 2
        assert set(mixed_standards) == set(
            [TokenStandard.ERC721, TokenStandard.ERC1155]
        )
