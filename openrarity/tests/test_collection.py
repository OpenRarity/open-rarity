from openrarity.models.chain import Chain
from openrarity.models.collection import Collection
from openrarity.models.token_metadata import StringAttributeValue


class TestCollection:
    def test_extract_null_attributes(self):
        attributes = {"attribute1": {"value1": 20, "value2": 30}}
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

        assert test_collection.extract_null_attributes == {
            "attribute1": StringAttributeValue("attribute1", "Null", 50)
        }
