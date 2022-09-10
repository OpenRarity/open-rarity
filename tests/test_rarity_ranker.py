from open_rarity.models.collection import Collection
from open_rarity.models.token_rarity import TokenRarity
from open_rarity.rarity_ranker import RarityRanker
from tests.helpers import generate_collection_with_token_traits


class TestRarityRanker:
    def test_rarity_ranker_empty_collection(self) -> None:
        assert RarityRanker.rank_collection(collection=None) is None

    def test_rarity_ranker_one_item(self) -> None:

        test_collection: Collection = generate_collection_with_token_traits(
            [{"trait1": "value1"}]  # Token 0
        )

        ranked_collection: Collection = RarityRanker.rank_collection(
            collection=test_collection
        )

        assert ranked_collection.tokens[0].token_rarity == TokenRarity(
            score=0, rank=1
        )

    def test_rarity_ranker_unique_scores(self) -> None:

        test_collection: Collection = generate_collection_with_token_traits(
            [
                {"trait1": "value1", "trait2": "value1"},  # Token 0
                {"trait1": "value1", "trait2": "value2"},  # Token 1
                {
                    "trait1": "value2",
                    "trait2": "value2",
                    "trait3": " value3",
                },  # Token 3
            ]
        )

        ranked_collection: Collection = RarityRanker.rank_collection(
            collection=test_collection
        )

        tokens = ranked_collection.tokens

        assert tokens[0].token_identifier.token_id == 2
        assert tokens[0].token_rarity == TokenRarity(
            score=1.3629912289393598, rank=1
        )

        assert tokens[1].token_identifier.token_id == 0
        assert tokens[1].token_rarity == TokenRarity(
            score=1.0000000000000002, rank=2
        )

        assert tokens[2].token_identifier.token_id == 1
        assert tokens[2].token_rarity == TokenRarity(
            score=0.6370087710606406, rank=3
        )

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

        ranked_collection: Collection = RarityRanker.rank_collection(
            collection=test_collection
        )

        tokens = ranked_collection.tokens
        print(
            [
                (
                    t.token_identifier.token_id,
                    t.token_rarity.score,
                    t.token_rarity.rank,
                )
                for t in ranked_collection.tokens
            ]
        )

        assert tokens[0].token_identifier.token_id == 4
        assert tokens[0].token_rarity == TokenRarity(
            score=1.3926137488801251, rank=1
        )

        assert tokens[1].token_identifier.token_id == 3
        assert tokens[1].token_rarity == TokenRarity(
            score=1.1338031424711967, rank=2
        )

        assert tokens[2].token_identifier.token_id == 0
        assert tokens[2].token_rarity == TokenRarity(
            score=0.8749925360622679, rank=3
        )

        assert tokens[3].token_identifier.token_id == 1
        assert tokens[3].token_rarity == TokenRarity(
            score=0.8749925360622679, rank=3
        )

        assert tokens[4].token_identifier.token_id == 2
        assert tokens[4].token_rarity == TokenRarity(
            score=0.7235980365241422, rank=5
        )
