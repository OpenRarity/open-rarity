from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_identifier import (
    EVMContractTokenIdentifier,
    SolanaMintAddressTokenIdentifier,
)
from open_rarity.models.token_metadata import TokenMetadata
from open_rarity.models.token_ranking_features import TokenRankingFeatures
from open_rarity.models.token_rarity import TokenRarity
from open_rarity.rarity_ranker import RarityRanker
from open_rarity.scoring.scorer import Scorer
from tests.helpers import generate_collection_with_token_traits


def verify_token_rarities(token_rarities: list[TokenRarity], expected_data: list[dict]):
    """
    Parameters
    ----------
    expected_data: list[dict]
        must be a list of dicts with the following keys:
        - id (token id)
        - unique_traits
        - rank
        - score (optional)
    """
    for token_rarity, expected in zip(token_rarities, expected_data):
        assert token_rarity.rank == expected["rank"]
        assert token_rarity.token.token_identifier.token_id == expected["id"]
        assert (
            token_rarity.token_features.unique_attribute_count
            == expected["unique_traits"]
        )
        if "score" in expected:
            assert token_rarity.score == expected["score"]


class TestRarityRanker:
    def test_rarity_ranker_empty_collection(self) -> None:
        assert RarityRanker.rank_collection(collection=None) == []
        assert (
            RarityRanker.rank_collection(
                collection=Collection(attributes_frequency_counts={}, tokens=[])
            )
            == []
        )

    def test_rarity_ranker_one_item(self) -> None:
        test_collection: Collection = generate_collection_with_token_traits(
            [{"trait1": "value1"}]  # Token 0
        )

        tokens: list[TokenRarity] = RarityRanker.rank_collection(
            collection=test_collection
        )

        assert tokens[0].score == 0
        assert tokens[0].rank == 1

    def test_rank_solana_collection(self) -> None:
        test_collection = generate_collection_with_token_traits(
            [{"trait1": "value1"}],
            token_identifier_type=SolanaMintAddressTokenIdentifier.identifier_type,
        )
        tokens: list[TokenRarity] = RarityRanker.rank_collection(
            collection=test_collection
        )

        assert tokens[0].score == 0
        assert tokens[0].rank == 1

    def test_rarity_ranker_equal_score_and_unique_trait(self) -> None:
        test_collection = generate_collection_with_token_traits(
            [
                # Token 0
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value1",  # unique trait
                    "trait3": "value2",  # 75%
                },
                # Token 1
                {
                    "trait1": "value1",  # 75%
                    "trait2": "value2",  # 75%
                    "trait3": "value2",  # 50%
                },
                # Token 2
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value2",  # 75%
                    "trait3": "value3",  # unique trait
                },
                # Token 3
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value2",  # 75%
                    "trait3": "value2",  # 75%
                    "trait4": "value1",  # unique trait
                },
            ]
        )

        token_rarities = RarityRanker.rank_collection(collection=test_collection)
        expected_tokens_in_rank_order = [
            {"id": 3, "unique_traits": 2, "rank": 1},
            {"id": 0, "unique_traits": 1, "rank": 2},
            {"id": 2, "unique_traits": 1, "rank": 2},
            {"id": 1, "unique_traits": 0, "rank": 4},
        ]
        verify_token_rarities(token_rarities, expected_tokens_in_rank_order)

    def test_rarity_ranker_unique_scores(self) -> None:
        test_collection = generate_collection_with_token_traits(
            [
                # Token 0
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value1",  # unique trait
                    "trait3": "value2",  # 75%
                },
                # Token 1
                {
                    "trait1": "value1",  # 75%
                    "trait2": "value2",  # 50%
                    "trait3": "value2",  # 50%
                },
                # Token 2
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value2",  # 50%
                    "trait3": "value3",  # unique trait
                },
                # Token 3
                {
                    "trait1": "value1",  # 100%
                    "trait2": "value4",  # unique trait
                    "trait3": "value2",  # 50%
                    "trait4": "value1",  # unique trait
                },  # Token 3
            ]
        )

        token_rarities = RarityRanker.rank_collection(test_collection)
        scorer = Scorer()
        expected_scores = scorer.score_collection(test_collection)
        expected_tokens_in_rank_order = [
            {
                "id": 3,
                "unique_traits": 3,
                "rank": 1,
                "score": expected_scores[3],
            },
            {
                "id": 2,
                "unique_traits": 1,
                "rank": 2,
                "score": expected_scores[2],
            },
            {
                "id": 0,
                "unique_traits": 1,
                "rank": 3,
                "score": expected_scores[0],
            },
            {
                "id": 1,
                "unique_traits": 0,
                "rank": 4,
                "score": expected_scores[1],
            },
        ]
        verify_token_rarities(token_rarities, expected_tokens_in_rank_order)

    def test_rarity_ranker_same_scores(self) -> None:
        test_collection: Collection = generate_collection_with_token_traits(
            [
                {
                    "trait1": "value1",
                    "trait2": "value1",
                    "trait3": "value1",
                },  # 0
                {
                    "trait1": "value1",
                    "trait2": "value1",
                    "trait3": "value1",
                },  # 1
                {
                    "trait1": "value2",
                    "trait2": "value1",
                    "trait3": "value3",
                },  # 2
                {
                    "trait1": "value2",
                    "trait2": "value2",
                    "trait3": "value3",
                },  # 3
                {
                    "trait1": "value3",
                    "trait2": "value3",
                    "trait3": "value3",
                },  # 4
            ]
        )

        token_rarities = RarityRanker.rank_collection(test_collection)

        expected_tokens_in_rank_order = [
            {"id": 4, "unique_traits": 2, "rank": 1, "score": 1.3926137488801251},
            {"id": 3, "unique_traits": 1, "rank": 2, "score": 1.1338031424711967},
            {"id": 0, "unique_traits": 0, "rank": 3, "score": 0.8749925360622679},
            {"id": 1, "unique_traits": 0, "rank": 3, "score": 0.8749925360622679},
            {"id": 2, "unique_traits": 0, "rank": 5, "score": 0.7235980365241422},
        ]
        verify_token_rarities(token_rarities, expected_tokens_in_rank_order)

    def test_set_ranks_same_unique_different_ic_score(self):
        token_rarities: list[TokenRarity] = []
        metadata = TokenMetadata({}, {}, {})

        token_rarities.append(
            TokenRarity(
                token=Token(
                    token_identifier=EVMContractTokenIdentifier(
                        token_id=1, contract_address="null"
                    ),
                    token_standard="ERC-721",
                    metadata=metadata,
                ),
                score=1.5,
                token_features=TokenRankingFeatures(unique_attribute_count=1),
            )
        )

        token_rarities.append(
            TokenRarity(
                token=Token(
                    token_identifier=EVMContractTokenIdentifier(
                        token_id=2, contract_address="null"
                    ),
                    token_standard="ERC-721",
                    metadata=metadata,
                ),
                score=1.5,
                token_features=TokenRankingFeatures(unique_attribute_count=2),
            )
        )

        token_rarities.append(
            TokenRarity(
                token=Token(
                    token_identifier=EVMContractTokenIdentifier(
                        token_id=3, contract_address="null"
                    ),
                    token_standard="ERC-721",
                    metadata=metadata,
                ),
                score=0.2,
                token_features=TokenRankingFeatures(unique_attribute_count=3),
            )
        )

        token_rarities.append(
            TokenRarity(
                token=Token(
                    token_identifier=EVMContractTokenIdentifier(
                        token_id=4, contract_address="null"
                    ),
                    token_standard="ERC-721",
                    metadata=metadata,
                ),
                score=7.0,
                token_features=TokenRankingFeatures(unique_attribute_count=0),
            )
        )

        result = RarityRanker.set_rarity_ranks(token_rarities)

        assert result[0].token.token_identifier.token_id == 3
        assert result[0].rank == 1

        assert result[1].token.token_identifier.token_id == 2
        assert result[1].rank == 2

        assert result[2].token.token_identifier.token_id == 1
        assert result[2].rank == 2

        assert result[3].token.token_identifier.token_id == 4
        assert result[3].rank == 4
