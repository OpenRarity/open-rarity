import pytest
from tests.helpers import generate_collection_with_token_traits
from open_rarity import OpenRarityScorer


class TestScorer:
    def test_score_collections_string_attributes(self):
        collection = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "pants", "hat": "cap", "special": "false"},
            ]
        )

        scorer = OpenRarityScorer()
        scores = scorer.score_collection(collection)
        assert len(scores) == 5

    def test_score_collection_with_numeric_attribute_errors(self):
        with pytest.raises(ValueError) as excinfo:
            collection = generate_collection_with_token_traits(
                [
                    {"bottom": "1", "hat": "1", "special": "true"},
                    {"bottom": "1", "hat": "1", "special": "false"},
                    {"bottom": "2", "hat": "2", "special": "false"},
                    {"bottom": "2", "hat": "2", "special": "false"},
                    {"bottom": 3, "hat": 2, "special": "false"},
                ]
            )

            scorer = OpenRarityScorer()
            scorer.score_collection(collection)

        assert (
            "OpenRarity currently does not support collections "
            "with numeric or date traits" in str(excinfo.value)
        )
