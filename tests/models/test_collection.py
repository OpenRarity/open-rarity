from open_rarity.models.collection import (
    TRAIT_COUNT_ATTRIBUTE_NAME,
    Collection,
    CollectionAttribute,
)
from open_rarity.models.token import Token
from open_rarity.models.token_metadata import StringAttribute, TokenMetadata
from open_rarity.models.token_standard import TokenStandard
from tests.helpers import (
    create_evm_token,
    create_numeric_evm_token,
    create_string_evm_token,
    generate_mixed_collection,
)


class TestCollection:
    evm_token = create_evm_token(
        token_id=1, metadata=TokenMetadata.from_attributes({"hat": "cap"})
    )

    attributes = {
        "hat": {"blue": 20, "red": 60},
        "pants": {"jeans": 10, "sweats": 70},
    }
    tokens_with_attributes: list[Token] = [
        create_evm_token(
            token_id=i,
            metadata=TokenMetadata.from_attributes(
                {}
                if i >= 80
                else {
                    "hat": "blue" if i < 20 else "red",
                    "pants": "jeans" if i < 10 else "sweats",
                }
            ),
        )
        for i in range(100)
    ]

    test_collection_attributes: Collection = Collection(
        name="collection with attributes mix",
        tokens=tokens_with_attributes,
    )

    tokens_no_attributes: list[Token] = [
        create_evm_token(token_id=i) for i in range(100)
    ]

    test_collection_no_attributes: Collection = Collection(
        name="collection with tokens but no attributes",
        tokens=tokens_no_attributes,
    )

    # All tokens have same attribute
    tokens_mixed_type_attributes: list[Token] = [
        create_string_evm_token(token_id=i) for i in range(50)
    ] + [create_numeric_evm_token(token_id=i) for i in range(50, 100)]

    test_numeric_attributes_collection: Collection = Collection(
        name="collection with uniform string and numeric attributes",
        tokens=tokens_mixed_type_attributes,
    )

    test_mixed_erc_collection: Collection = Collection(
        name="test4",
        tokens=[create_evm_token(token_id=i) for i in range(10)]
        + [
            create_evm_token(token_id=i, token_standard=TokenStandard.ERC1155)
            for i in range(10, 50)
        ]
        + [create_evm_token(token_id=i) for i in range(50, 60)],
    )

    test_erc1155_collection: Collection = Collection(
        name="test4",
        tokens=[
            create_evm_token(token_id=i, token_standard=TokenStandard.ERC1155)
            for i in range(10)
        ],
    )

    def test_tokens(self):
        collection_one_token = Collection(tokens=[self.evm_token])
        assert self.test_collection_attributes.tokens == self.tokens_with_attributes
        assert self.test_collection_no_attributes.tokens == self.tokens_no_attributes
        assert (
            self.test_numeric_attributes_collection.tokens
            == self.tokens_mixed_type_attributes
        )
        assert collection_one_token.tokens == [self.evm_token]

        assert self.test_collection_attributes.token_total_supply == 100
        assert self.test_collection_no_attributes.token_total_supply == 100
        assert self.test_numeric_attributes_collection.token_total_supply == 100
        assert collection_one_token.token_total_supply == 1

        assert collection_one_token.attributes_frequency_counts == {
            "hat": {"cap": 1},
            TRAIT_COUNT_ATTRIBUTE_NAME: {"1": 1},
        }
        assert self.test_collection_no_attributes.attributes_frequency_counts == {
            TRAIT_COUNT_ATTRIBUTE_NAME: {"0": 100}
        }
        assert self.test_collection_attributes.attributes_frequency_counts == {
            **self.attributes,
            TRAIT_COUNT_ATTRIBUTE_NAME: {"2": 80, "0": 20},
        }

    def test_extract_null_attributes(self):
        assert self.test_collection_attributes.extract_null_attributes() == {
            "hat": CollectionAttribute(StringAttribute("hat", "Null"), 20),
            "pants": CollectionAttribute(StringAttribute("pants", "Null"), 20),
        }

    def test_extract_null_attributes_empty(self):
        all_attributes = Collection(
            tokens=self.tokens_with_attributes[0:80],
        )
        assert all_attributes.extract_null_attributes() == {}
        assert self.test_collection_no_attributes.extract_null_attributes() == {}

    def test_extract_collection_attributes(self):
        assert self.test_collection_attributes.extract_collection_attributes() == {
            "hat": [
                CollectionAttribute(StringAttribute("hat", "blue"), 20),
                CollectionAttribute(StringAttribute("hat", "red"), 60),
            ],
            "pants": [
                CollectionAttribute(StringAttribute("pants", "jeans"), 10),
                CollectionAttribute(StringAttribute("pants", "sweats"), 70),
            ],
            TRAIT_COUNT_ATTRIBUTE_NAME: [
                CollectionAttribute(
                    StringAttribute(TRAIT_COUNT_ATTRIBUTE_NAME, "2"), 80
                ),
                CollectionAttribute(
                    StringAttribute(TRAIT_COUNT_ATTRIBUTE_NAME, "0"), 20
                ),
            ],
        }

    def test_extract_empty_collection_attributes(self):
        assert self.test_collection_no_attributes.extract_collection_attributes() == {
            TRAIT_COUNT_ATTRIBUTE_NAME: [
                CollectionAttribute(
                    StringAttribute(TRAIT_COUNT_ATTRIBUTE_NAME, "0"), 100
                )
            ]
        }

    def test_has_numeric_attributes(self):
        assert self.test_numeric_attributes_collection.has_numeric_attribute
        assert not self.test_collection_attributes.has_numeric_attribute

    def test_collection_init(self):
        collection = Collection(
            tokens=[
                create_evm_token(
                    token_id=1,
                    metadata=TokenMetadata.from_attributes(
                        {
                            "hat": "cap",
                            "bottom": "jeans",
                            "something another": "special",
                        }
                    ),
                ),
                create_evm_token(
                    token_id=2,
                    metadata=TokenMetadata.from_attributes(
                        {
                            "hat": "cap",
                            "bottom": "pjs",
                            "something another": "not special",
                        }
                    ),
                ),
                create_evm_token(
                    token_id=2,
                    metadata=TokenMetadata.from_attributes(
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
            TRAIT_COUNT_ATTRIBUTE_NAME: {"3": 3},
        }

    def test_init_no_trait_count(self):
        tokens = [
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "bottom": "jeans",
                        "something another": "special",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "something another": "not special",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                    }
                ),
            ),
        ]
        collection = Collection(tokens=tokens)
        assert collection.attributes_frequency_counts == {
            "hat": {"cap": 2, "bucket hat": 2},
            "bottom": {"jeans": 1},
            "something another": {"special": 1, "not special": 1},
            "new": {"very special": 2},
            "four": {"four value": 2},
            TRAIT_COUNT_ATTRIBUTE_NAME: {"3": 1, "2": 1, "4": 2},
        }

    def test_init_trait_count_diff_name_exists(self):
        tokens = [
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "bottom": "jeans",
                        "something another": "special",
                        "TRAIT_COUNT": "3",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "something another": "not special",
                        "TRAIT_COUNT": "2",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                        "TRAIT_COUNT": "4",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                        "TRAIT_COUNT": "4",
                    }
                ),
            ),
        ]
        collection = Collection(tokens=tokens)
        assert collection.attributes_frequency_counts == {
            "hat": {"cap": 2, "bucket hat": 2},
            "bottom": {"jeans": 1},
            "something another": {"special": 1, "not special": 1},
            "new": {"very special": 2},
            "four": {"four value": 2},
            "trait_count": {"3": 1, "2": 1, "4": 2},
            TRAIT_COUNT_ATTRIBUTE_NAME: {"3": 1, "4": 1, "5": 2},
        }

    def test_init_trait_count_exists(self):
        tokens = [
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "bottom": "jeans",
                        "something another": "special",
                        TRAIT_COUNT_ATTRIBUTE_NAME: "3",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "cap",
                        "something another": "not special",
                        TRAIT_COUNT_ATTRIBUTE_NAME: "2",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                        TRAIT_COUNT_ATTRIBUTE_NAME: "4",
                    }
                ),
            ),
            create_evm_token(
                token_id=2,
                metadata=TokenMetadata.from_attributes(
                    {
                        "hat": "bucket hat",
                        "new": "very special",
                        "integer trait - will not be shown": 1,
                        "four": "four value",
                        TRAIT_COUNT_ATTRIBUTE_NAME: "4",
                    }
                ),
            ),
        ]
        collection = Collection(tokens=tokens)
        assert collection.attributes_frequency_counts == {
            "hat": {"cap": 2, "bucket hat": 2},
            "bottom": {"jeans": 1},
            "something another": {"special": 1, "not special": 1},
            "new": {"very special": 2},
            "four": {"four value": 2},
            TRAIT_COUNT_ATTRIBUTE_NAME: {"3": 1, "2": 1, "4": 2},
        }

    def test_collection_init_equality(self):
        large_collection = generate_mixed_collection()
        comparable_collection = Collection(tokens=large_collection.tokens)
        assert (
            comparable_collection.attributes_frequency_counts
            == large_collection.attributes_frequency_counts
        )

    def test_token_standards(self):
        assert self.test_collection_attributes.token_standards == [TokenStandard.ERC721]
        assert self.test_collection_no_attributes.token_standards == [
            TokenStandard.ERC721
        ]
        assert self.test_erc1155_collection.token_standards == [TokenStandard.ERC1155]

        # Test mixed collection
        mixed_standards = self.test_mixed_erc_collection.token_standards
        assert len(mixed_standards) == 2
        assert set(mixed_standards) == set(
            [TokenStandard.ERC721, TokenStandard.ERC1155]
        )
