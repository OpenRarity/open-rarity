import pytest
from open_rarity import OpenRarityScorer, Collection, TokenStandard
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from tests.helpers import (
    generate_collection_with_token_traits,
    create_evm_token,
)


class TestScorer:
    def test_init_settings(self):
        scorer = OpenRarityScorer()
        assert isinstance(scorer.handler, InformationContentScoringHandler)

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

    def test_score_collection_with_erc1155_errors(self):
        with pytest.raises(ValueError) as excinfo:
            collection = Collection(
                name="test",
                tokens=[
                    create_evm_token(
                        token_id=i, token_standard=TokenStandard.ERC1155
                    )
                    for i in range(10)
                ],
                attributes_frequency_counts={},
            )
            scorer = OpenRarityScorer()
            scorer.score_collection(collection)

        assert (
            "OpenRarity currently does not support non-ERC721 collections"
            in str(excinfo.value)
        )
