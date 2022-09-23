from open_rarity.models.collection import Collection
from open_rarity.models.token_rarity import TokenRarity
from open_rarity.rarity_ranker import RarityRanker
from tests.helpers import generate_collection_with_token_traits


class TestRarityRanker:
    def test_rarity_ranker_empty_collection(self) -> None:
        assert RarityRanker.rank_collection(collection=None) == []
        assert (
            RarityRanker.rank_collection(
                collection=Collection(
                    attributes_frequency_counts={}, tokens=[]
                )
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

    def test_rarity_ranker_unique_scores(self) -> None:

        test_collection: Collection = generate_collection_with_token_traits(
            [
                {"trait1": "value1", "trait2": "value1"},  # Token 0
                {"trait1": "value1", "trait2": "value2"},  # Token 1
                {
                    "trait1": "value2",
                    "trait2": "value2",
                    "trait3": " value3",
                },  # Token 2
            ]
        )

        tokens: list[TokenRarity] = RarityRanker.rank_collection(
            collection=test_collection
        )

        assert tokens[0].token.token_identifier.token_id == 2
        assert tokens[0].score == 2.513646200858506
        assert tokens[0].rank == 1

        assert tokens[1].token.token_identifier.token_id == 0
        assert tokens[1].score == 1.5753274859595732
        assert tokens[1].rank == 2

        assert tokens[2].token.token_identifier.token_id == 1
        assert tokens[2].score == 0.6370087710606406
        assert tokens[2].rank == 3

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

        tokens: list[TokenRarity] = RarityRanker.rank_collection(
            collection=test_collection
        )

        assert tokens[0].token.token_identifier.token_id == 4
        assert tokens[0].score == 2.594492985431578
        assert tokens[0].rank == 1

        assert tokens[1].token.token_identifier.token_id == 3
        assert tokens[1].score == 1.7347427607469232
        assert tokens[1].rank == 2

        assert tokens[2].token.token_identifier.token_id == 0
        assert tokens[2].score == 0.8749925360622679
        assert tokens[2].rank == 3

        assert tokens[3].token.token_identifier.token_id == 1
        assert tokens[3].score == 0.8749925360622679
        assert tokens[3].rank == 3

        assert tokens[4].token.token_identifier.token_id == 2
        assert tokens[4].score == 0.7235980365241422
        assert tokens[4].rank == 5
