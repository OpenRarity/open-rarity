from openrarity.models.chain import Chain
from openrarity.models.collection import Collection
from openrarity.models.token_metadata import StringAttributeValue


class TestCollection:

    attributes = {
        "attribute1": {"value1": 20, "value2": 30},
        "attribute2": {"value1": 10, "value2": 50},
    }
    test_collection: Collection = Collection(
        "test",
        "test",
        "test-address",
        "test-address",
        "ERC-721",
        Chain.ETH,
        100,
        [],
        attributes,
    )

    test_no_attributes_collection: Collection = Collection(
        "test",
        "test",
        "test-address",
        "test-address",
        "ERC-721",
        Chain.ETH,
        100,
        [],
        {},
    )

    def test_extract_null_attributes(self):

        assert self.test_collection.extract_null_attributes == {
            "attribute1": StringAttributeValue("attribute1", "Null", 50),
            "attribute2": StringAttributeValue("attribute2", "Null", 40),
        }

    def test_extract_null_attributes_empty(self):

        assert self.test_no_attributes_collection.extract_null_attributes == {}

    def test_extract_collection_attributes(self):

        assert self.test_collection.extract_collection_attributes == {
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
            self.test_no_attributes_collection.extract_collection_attributes
            == {}
        )
