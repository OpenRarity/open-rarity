from open_rarity.models.token_metadata import (
    NumericAttribute,
    StringAttribute,
    TokenMetadata,
)

from tests.helpers import create_evm_token


class TestToken:
    def test_token_init_metadata_non_matching_attribute_names(self):
        token = create_evm_token(
            token_id=1,
            metadata=TokenMetadata(
                string_attributes={
                    "hat": StringAttribute(name="big hat", value="blue"),
                    "shirt": StringAttribute(name=" shirt", value="red"),
                }
            ),
        )
        assert token.metadata.string_attributes == {
            "hat": StringAttribute(name="hat", value="blue"),
            "shirt": StringAttribute(name="shirt", value="red"),
        }

    def test_token_attribute_normalization(self):
        expected_equal_metadata_tokens = [
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat ": StringAttribute(name="hat", value="blue"),
                        "Shirt ": StringAttribute(name="shirt", value="red"),
                    },
                    numeric_attributes={
                        "level": NumericAttribute(name="level", value=1),
                    },
                ),
            ),
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat": StringAttribute(name="hat", value="blue"),
                        "Shirt ": StringAttribute(name=" shirt", value="red"),
                    },
                    numeric_attributes={
                        "Level": NumericAttribute(name="level", value=1),
                    },
                ),
            ),
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        "Hat": StringAttribute(name=" hat ", value="blue"),
                        "shirt": StringAttribute(name="shirt", value="red"),
                    },
                    numeric_attributes={
                        "Level": NumericAttribute(name=" level ", value=1),
                    },
                ),
            ),
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        "  hat ": StringAttribute(name=" hat ", value="blue"),
                        "   shirt": StringAttribute(name="shirt", value="red"),
                    },
                    numeric_attributes={
                        "level": NumericAttribute(name="level ", value=1),
                    },
                ),
            ),
        ]

        assert all(
            t.metadata == expected_equal_metadata_tokens[0].metadata
            for t in expected_equal_metadata_tokens
        )

        expected_not_equal = [
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        " big hat ": StringAttribute(
                            name=" hat ", value="blue"
                        ),
                        "   shirt": StringAttribute(name="shirt", value="red"),
                    },
                    numeric_attributes={
                        "level": NumericAttribute(name="level", value=1),
                    },
                ),
            ),
            create_evm_token(
                token_id=1,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat": StringAttribute(name="hat", value="blue"),
                        "shirt": StringAttribute(name="shirt", value="red"),
                    },
                    numeric_attributes={
                        "big level": NumericAttribute(name="level", value=1),
                    },
                ),
            ),
        ]

        assert all(
            t.metadata != expected_equal_metadata_tokens[0].metadata
            for t in expected_not_equal
        )
