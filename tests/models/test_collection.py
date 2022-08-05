from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_standard import TokenStandard
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import TokenMetadata, StringAttributeValue


def create_evm_token(
    token_id: int,
    contract_address: str = "0xaaa",
    token_standard: TokenStandard = TokenStandard.ERC721,
    metadata: TokenMetadata = TokenMetadata(),
) -> Token:
    return Token(
        token_identifier=EVMContractTokenIdentifier(contract_address=contract_address, token_id=token_id),
        token_standard=token_standard,
        metadata=metadata,
    )


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

    def test_tokens(self):
        assert self.test_collection.tokens == self.tokens
        assert self.test_no_attributes_collection.tokens == self.tokens
        assert self.test_collection.token_total_supply == 100
        assert self.test_no_attributes_collection.token_total_supply == 100

        new_tokens = [create_evm_token(token_id=100_000)]
        self.test_collection.tokens = new_tokens
        assert self.test_collection.tokens == new_tokens

        self.test_no_attributes_collection.tokens = []
        assert self.test_collection.tokens == []
        assert self.test_collection.token_total_supply == 1
        assert self.test_no_attributes_collection.token_total_supply == 0

    def test_extract_null_attributes(self):
        assert self.test_collection.extract_null_attributes == {
            "attribute1": StringAttributeValue("attribute1", "Null", 50),
            "attribute2": StringAttributeValue("attribute2", "Null", 40),
        }

    def test_extract_null_attributes_empty(self):
        assert self.test_no_attributes_collection.extract_null_attributes == {}

    def test_extract_collection_attributes(self):
        assert self.test_collection.extract_collection_attributes() == {
            "attribute1": [
                StringAttributeValue("attribute1", "value1", 20),
                StringAttributeValue("attribute1", "value2", 30),
            ],
            "attribute2": [
                StringAttributeValue("attribute2", "value1", 10),
                StringAttributeValue("attribute2", "value2", 50),
            ],
        }

    def test_extract_empty_collection_attributes(self):
        assert self.test_no_attributes_collection.extract_collection_attributes() == {}
