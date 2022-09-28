from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_features import TokenFeatures
from open_rarity.models.token_identifier import (
    EVMContractTokenIdentifier,
)
from open_rarity.models.token_metadata import TokenMetadata
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
                {
                    "trait1": "value1",
                    "trait2": "value1",
                    "trait3": "value2",
                },  # Token 0
                {
                    "trait1": "value1",
                    "trait2": "value2",
                    "trait3": "value2",
                },  # Token 1
                {
                    "trait1": "value1",
                    "trait2": "value2",
                    "trait3": " value3",
                },  # Token 2
                {
                    "trait1": "value1",
                    "trait2": "value4",
                    "trait3": " value2",
                    "trait4": " value1",
                },  # Token 3
            ]
        )

        tokens: list[TokenRarity] = RarityRanker.rank_collection(
            collection=test_collection
        )
        print(tokens[0].token_features.unique_attribute_count)
        print(tokens[1].token_features.unique_attribute_count)
        print(tokens[2].token_features.unique_attribute_count)
        print(tokens[3].token_features.unique_attribute_count)

        print(tokens[0].score)
        print(tokens[1].score)
        print(tokens[2].score)
        print(tokens[3].score)

        assert tokens[0].token.token_identifier.token_id == 3
        assert tokens[0].score == 1.4139176838874645
        assert tokens[0].rank == 1
        assert tokens[0].token_features.unique_attribute_count == 2

        assert tokens[1].token.token_identifier.token_id == 2
        assert tokens[1].score == 1.0936672479356941
        assert tokens[1].rank == 2
        assert tokens[1].token_features.unique_attribute_count == 1

        assert tokens[2].token.token_identifier.token_id == 0
        assert tokens[2].score == 0.906332752064306
        assert tokens[2].rank == 3
        assert tokens[2].token_features.unique_attribute_count == 1

        assert tokens[3].token.token_identifier.token_id == 1
        assert tokens[3].score == 0.5860823161125354
        assert tokens[3].rank == 4
        assert tokens[3].token_features.unique_attribute_count == 0

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
        assert tokens[0].score == 1.3926137488801251
        assert tokens[0].rank == 1
        assert tokens[0].token_features.unique_attribute_count == 2

        assert tokens[1].token.token_identifier.token_id == 3
        assert tokens[1].score == 1.1338031424711967
        assert tokens[1].rank == 2
        assert tokens[1].token_features.unique_attribute_count == 1

        assert tokens[2].token.token_identifier.token_id == 0
        assert tokens[2].score == 0.8749925360622679
        assert tokens[2].rank == 3
        assert tokens[2].token_features.unique_attribute_count == 0

        assert tokens[3].token.token_identifier.token_id == 1
        assert tokens[3].score == 0.8749925360622679
        assert tokens[3].rank == 3
        assert tokens[3].token_features.unique_attribute_count == 0

        assert tokens[4].token.token_identifier.token_id == 2
        assert tokens[4].score == 0.7235980365241422
        assert tokens[4].rank == 5
        assert tokens[4].token_features.unique_attribute_count == 0

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
                token_features=TokenFeatures(unique_attribute_count=1),
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
                token_features=TokenFeatures(unique_attribute_count=2),
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
                token_features=TokenFeatures(unique_attribute_count=3),
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
                token_features=TokenFeatures(unique_attribute_count=0),
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
