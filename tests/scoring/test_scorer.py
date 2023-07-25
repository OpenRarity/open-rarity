import pytest

from open_rarity import Collection, OpenRarityScorer, TokenStandard
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from tests.helpers import create_evm_token, generate_collection_with_token_traits


class TestScorer:
    scorer = OpenRarityScorer()

    def test_init_settings(self):
        assert isinstance(self.scorer.handler, InformationContentScoringHandler)

    def test_score_collections_with_string_attributes(self):
        collection = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "pants", "hat": "cap", "special": "false"},
            ]
        )

        collection_two = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "pants", "hat": "cap", "special": "false"},
            ]
        )

        scores = self.scorer.score_collection(collection)
        assert len(scores) == 5

        scores = self.scorer.score_tokens(collection, collection.tokens)
        assert len(scores) == 5

        scores = self.scorer.score_collections([collection, collection_two])
        assert len(scores[0]) == 5
        assert len(scores[1]) == 5

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

    def test_score_collection_with_erc1155_errors(self):
        with pytest.raises(ValueError) as excinfo:
            collection = Collection(
                name="test",
                tokens=[
                    create_evm_token(token_id=i, token_standard=TokenStandard.ERC1155)
                    for i in range(10)
                ],
                attributes_frequency_counts={},
            )
            scorer = OpenRarityScorer()
            scorer.score_collection(collection)

        assert (
            "OpenRarity currently only supports ERC721/Non-fungible standards"
            in str(excinfo.value)
        )
