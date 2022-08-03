from open_rarity.models.chain import Chain
from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_standard import TokenStandard
from open_rarity.models.collection_identifier import OpenseaCollectionIdentifier
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import TokenMetadata, StringAttributeValue


class TestCollection:

    attributes = {
        "attribute1": {"value1": 20, "value2": 30},
        "attribute2": {"value1": 10, "value2": 50},
    }
    test_collection: Collection = Collection(
        identifier=OpenseaCollectionIdentifier(slug='test'),
        name="test",
        chain=Chain.ETH,
        _tokens=[
            Token(
                token_identifier=EVMContractTokenIdentifier(contract_address='0xaaa', token_id=i),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata()
            ) for i in range(100)
        ],
        attributes_distribution=attributes,
    )

    test_no_attributes_collection: Collection = Collection(
        identifier=OpenseaCollectionIdentifier(slug='test2'),
        name="test2",
        chain=Chain.ETH,
        _tokens=[
            Token(
                token_identifier=EVMContractTokenIdentifier(contract_address='0xabb', token_id=i),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata()
            ) for i in range(100)
        ],
        attributes_distribution={},
    )

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
        assert (
            self.test_no_attributes_collection.extract_collection_attributes()
            == {}
        )
