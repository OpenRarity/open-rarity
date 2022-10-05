from open_rarity.scoring.token_feature_extractor import TokenFeatureExtractor
from tests.helpers import generate_collection_with_token_traits


class TestFeatureExtractor:
    def test_feature_extractor(self):
        collection = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "3", "hat": "2", "special": "false"},
                {"bottom": "4", "hat": "3", "special": "false"},
            ]
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[0], collection=collection
            ).unique_attribute_count
            == 1
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[1], collection=collection
            ).unique_attribute_count
            == 0
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[2], collection=collection
            ).unique_attribute_count
            == 0
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[3], collection=collection
            ).unique_attribute_count
            == 0
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[4], collection=collection
            ).unique_attribute_count
            == 1
        )

        assert (
            TokenFeatureExtractor.extract_unique_attribute_count(
                token=collection.tokens[5], collection=collection
            ).unique_attribute_count
            == 2
        )
