from random import sample

from open_rarity.models.collection import TRAIT_COUNT_ATTRIBUTE_NAME
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights
from tests.helpers import (
    generate_collection_with_token_traits,
    generate_mixed_collection,
    generate_onerare_rarity_collection,
    generate_uniform_rarity_collection,
    get_mixed_trait_spread,
)


class TestScoringUtils:
    mixed_collection = generate_mixed_collection()

    def test_get_token_attributes_scores_and_weights_timing_single(self):
        import time

        collection = self.mixed_collection
        start_time = time.time()
        get_token_attributes_scores_and_weights(
            collection=collection,
            token=collection.tokens[0],
            normalized=True,
        )
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"This is single time in seconds: {time_taken}")
        assert time_taken < 0.003

    def test_get_token_attributes_scores_and_weights_timing_avg(self):
        import time

        collection = self.mixed_collection
        tokens_to_test = sample(collection.tokens, 20)
        start_time = time.time()
        for token in tokens_to_test:
            get_token_attributes_scores_and_weights(
                collection=collection,
                token=token,
                normalized=True,
            )
        end_time = time.time()
        avg_time = (end_time - start_time) / 20
        print(f"This is avg time in seconds: {avg_time}")
        assert avg_time < 0.003

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
        # Note: Since trait count is automatically added, attributes are actually 6
        for token_to_test in uniform_tokens_to_test:
            scores, weights = get_token_attributes_scores_and_weights(
                collection=uniform_collection,
                token=token_to_test,
                normalized=True,
            )
            assert scores == [10] * 5 + [1.0]
            assert weights == [0.10] * 5 + [1.0]

            scores, weights = get_token_attributes_scores_and_weights(
                collection=uniform_collection,
                token=token_to_test,
                normalized=False,
            )
            assert scores == [10] * 5 + [1.0]
            assert weights == [1] * 6

    def test_get_token_attributes_scores_and_weights_one_rare(self):
        # The last token (#9999) has a unique attribute value for all
        # 5 different attribute types
        onerare_collection = generate_onerare_rarity_collection(
            attribute_count=3,
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
            assert scores == [10000 / 1111] * 3 + [1.0]
            assert weights == [0.10] * 3 + [1.0]

            scores, weights = get_token_attributes_scores_and_weights(
                collection=onerare_collection,
                token=token_to_test,
                normalized=False,
            )
            assert scores == [10000 / 1111] * 3 + [1.0]
            assert weights == [1] * 4

        # Verify the one rare token score
        rare_token = onerare_collection.tokens[9999]
        scores, weights = get_token_attributes_scores_and_weights(
            collection=onerare_collection,
            token=rare_token,
            normalized=True,
        )
        assert scores == [10000 / 1] * 3 + [1.0]
        assert weights == [0.10] * 3 + [1.0]

    def test_get_token_attributes_scores_and_weights_scores_vary(self):
        collection = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1"},
                {"bottom": "1", "hat": "1"},
                {"bottom": "1", "hat": "2"},
            ]
        )
        expected_scores = [
            [3 / 3, 3 / 2, 1.0],
            [3 / 3, 3 / 2, 1.0],
            [3 / 3, 3 / 1, 1.0],
        ]

        for i in range(collection.token_total_supply):
            scores, weights = get_token_attributes_scores_and_weights(
                collection=collection,
                token=collection.tokens[i],
                normalized=True,
            )
            assert scores == expected_scores[i]
            assert weights == [1, 0.5, 1]

    def test_get_token_attributes_scores_and_weights_score_mix(self):
        mixed_collection = self.mixed_collection
        tokens_to_test = sample(mixed_collection.tokens, 20)
        trait_spread = {
            **get_mixed_trait_spread(),
            TRAIT_COUNT_ATTRIBUTE_NAME: {"3": 10_000},
        }
        for token in tokens_to_test:
            scores, weights = get_token_attributes_scores_and_weights(
                collection=mixed_collection,
                token=token,
                normalized=True,
            )
            expected_scores = []
            expected_weights = []
            for attribute_name, str_attribute in sorted(
                token.metadata.string_attributes.items()
            ):
                num_tokens_with_trait = trait_spread[attribute_name][
                    str_attribute.value
                ]
                expected_scores.append(10000 / num_tokens_with_trait)
                expected_weights.append(1 / len(trait_spread[attribute_name]))

            assert scores == expected_scores
            assert weights == expected_weights

    def test_get_token_attributes_scores_and_weights_empty_attributes(self):
        collection_with_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "3", "hat": "2"},
            ]
        )
        expected_weights_with_null = [1 / 3, 1 / 2, 1 / 2, 1]

        collection_without_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "none"},
                {"bottom": "2", "hat": "2", "special": "none"},
                {"bottom": "2", "hat": "2", "special": "none"},
                {"bottom": "3", "hat": "2", "special": "none"},
            ]
        )
        expected_weights_without_null = [1 / 3, 1 / 2, 1 / 2, 1 / 2]
        expected_scores = [
            [5 / 2, 5 / 2, 5 / 1, 5 / 1],
            [5 / 2, 5 / 2, 5 / 4, 5 / 4],
            [5 / 2, 5 / 3, 5 / 4, 5 / 4],
            [5 / 2, 5 / 3, 5 / 4, 5 / 4],
            [5 / 1, 5 / 3, 5 / 4, 5 / 4],
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

    def test_get_token_attributes_scores_and_weights_null_attributes(self):
        collection_with_null_value = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "null"},
                {"bottom": "2", "hat": "2", "special": "null"},
                {"bottom": "2", "hat": "2", "special": "null"},
                {"bottom": "3", "hat": "2", "special": "null"},
            ]
        )
        expected_weights = [1 / 3, 1 / 2, 1, 1 / 2]
        expected_scores = [
            [5 / 2, 5 / 2, 1, 5 / 1],
            [5 / 2, 5 / 2, 1, 5 / 4],
            [5 / 2, 5 / 3, 1, 5 / 4],
            [5 / 2, 5 / 3, 1, 5 / 4],
            [5 / 1, 5 / 3, 1, 5 / 4],
        ]

        for i in range(collection_with_null_value.token_total_supply):
            scores, weights = get_token_attributes_scores_and_weights(
                collection=collection_with_null_value,
                token=collection_with_null_value.tokens[i],
                normalized=True,
            )
            assert scores == expected_scores[i]
            assert weights == expected_weights
