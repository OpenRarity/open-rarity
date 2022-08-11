from tests.utils import (
    generate_uniform_rarity_collection,
    generate_onerare_rarity_collection,
    generate_collection_with_token_traits,
)
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights


class TestScoringUtils:

    def test_get_token_attributes_scores_and_weights_uniform(self):
        uniform_collection = generate_uniform_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )
        uniform_tokens_to_test = [
            uniform_collection.tokens[0],
            uniform_collection.tokens[1405],
            uniform_collection.tokens[9999],
        ]
        for token_to_test in uniform_tokens_to_test:
            scores, weights = get_token_attributes_scores_and_weights(
                collection=uniform_collection,
                token=token_to_test,
                normalized=True,
            )
            assert scores == [10] * 5
            assert weights == [0.10] * 5

            scores, weights = get_token_attributes_scores_and_weights(
                collection=uniform_collection,
                token=token_to_test,
                normalized=False,
            )
            assert scores == [10] * 5
            assert weights == [1] * 5

    def test_get_token_attributes_scores_and_weights_one_rare(self):
        # The last token (#9999) has a unique attribute value for all
        # 5 different attribute types
        onerare_collection = generate_onerare_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )
        # Verify common tokens
        common_tokens_to_test = [
            onerare_collection.tokens[0],
            onerare_collection.tokens[5045],
            onerare_collection.tokens[9998],
        ]
        # Scores for common tokens are around ~9.0009
        for token_to_test in common_tokens_to_test:
            scores, weights = get_token_attributes_scores_and_weights(
                collection=onerare_collection,
                token=token_to_test,
                normalized=True,
            )
            assert scores == [10000 / 1111] * 5
            assert weights == [0.10] * 5

            scores, weights = get_token_attributes_scores_and_weights(
                collection=onerare_collection,
                token=token_to_test,
                normalized=False,
            )
            assert scores == [10000 / 1111] * 5
            assert weights == [1] * 5

        # Verify the one rare token score
        rare_token = onerare_collection.tokens[9999]
        scores, weights = get_token_attributes_scores_and_weights(
            collection=onerare_collection,
            token=rare_token,
            normalized=True,
        )
        assert scores == [10000 / 1] * 5
        assert weights == [0.10] * 5

    def test_get_token_attributes_scores_and_weights_scores_vary(self):
        collection = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1"},
                {"bottom": "1", "hat": "1"},
                {"bottom": "1", "hat": "2"},
            ]
        )
        expected_scores = [[3 / 3, 3 / 2], [3 / 3, 3 / 2], [3 / 3, 3 / 1]]

        for i in range(collection.token_total_supply):
            scores, weights = get_token_attributes_scores_and_weights(
                collection=collection,
                token=collection.tokens[i],
                normalized=True,
            )
            assert scores == expected_scores[i]
            assert weights == [1, 0.5]

    def test_get_token_attributes_scores_and_weights_null_attributes(self):
        collection_with_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "3", "hat": "2"},
            ]
        )
        expected_weights_with_null = [1 / 3, 1 / 2, 1]

        # TODO [vicky]: This is currently an open thread to be discussed
        # We may change it such that both of these collections have the
        # same weighting.
        collection_without_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "3", "hat": "2", "special": "false"},
            ]
        )
        expected_weights_without_null = [1 / 3, 1 / 2, 1 / 2]
        expected_scores = [
            [5 / 2, 5 / 2, 5 / 1],
            [5 / 2, 5 / 2, 5 / 4],
            [5 / 2, 5 / 3, 5 / 4],
            [5 / 2, 5 / 3, 5 / 4],
            [5 / 1, 5 / 3, 5 / 4],
        ]

        for collection, expected_weights in [
            [collection_with_null, expected_weights_with_null],
            [collection_without_null, expected_weights_without_null],
        ]:

            for i in range(collection.token_total_supply):
                scores, weights = get_token_attributes_scores_and_weights(
                    collection=collection,
                    token=collection.tokens[i],
                    normalized=True,
                )
                assert scores == expected_scores[i]
                assert weights == expected_weights
