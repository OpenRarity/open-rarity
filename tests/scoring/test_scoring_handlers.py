import time
from random import sample

import numpy as np
import pytest

from open_rarity.models.collection import TRAIT_COUNT_ATTRIBUTE_NAME, Collection
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from open_rarity.scoring.utils import get_token_attributes_scores_and_weights
from tests.helpers import (
    generate_collection_with_token_traits,
    generate_mixed_collection,
    get_mixed_trait_spread,
    onerare_rarity_tokens,
    uniform_rarity_tokens,
)


class TestScoringHandlers:
    max_scoring_time_for_10k_s = 2
    uniform_tokens = uniform_rarity_tokens(
        token_total_supply=10_000, attribute_count=5, values_per_attribute=10
    )

    uniform_collection = Collection(tokens=uniform_tokens)

    one_rare_tokens = onerare_rarity_tokens(
        token_total_supply=10_000,
        attribute_count=3,
        values_per_attribute=10,
    )

    # The last token (#9999) has a unique attribute value for all
    # 5 different attribute types
    onerare_collection = Collection(tokens=one_rare_tokens)

    # Collection with following attribute distribution
    # "hat":
    #   20% have "cap",
    #   30% have "beanie",
    #   45% have "hood",
    #   5% have "visor"
    # "shirt":
    #   80% have "white-t",
    #   20% have "vest"
    # "special":
    #   1% have "special"
    #   others none
    mixed_collection = generate_mixed_collection()

    def test_information_content_rarity_uniform(self):
        ic_handler = InformationContentScoringHandler()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_ic_rarity = 1.0
        assert np.round(
            ic_handler.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_ic_rarity, 8)

    def test_information_content_rarity_mixed(self):
        ic_scorer = InformationContentScoringHandler()

        # First test collection entropy
        collection_entropy = ic_scorer._get_collection_entropy(self.mixed_collection)
        collection_probs = []
        mixed_spread = get_mixed_trait_spread()
        for trait_dict in mixed_spread.values():
            for tokens_with_trait in trait_dict.values():
                collection_probs.append(tokens_with_trait / 10000)

        assert np.round(collection_entropy, 10) == np.round(
            -np.dot(collection_probs, np.log2(collection_probs)), 10
        )

        # Test the actual scores
        token_idxs_to_test = sample(range(self.mixed_collection.token_total_supply), 20)
        scores = ic_scorer.score_tokens(
            collection=self.mixed_collection,
            tokens=self.mixed_collection.tokens,
        )
        assert len(scores) == 10000
        for token_idx in token_idxs_to_test:
            token = self.mixed_collection.tokens[token_idx]
            score = scores[token_idx]
            assert score == ic_scorer.score_token(
                collection=self.mixed_collection,
                token=token,
            )
            attr_scores, _ = get_token_attributes_scores_and_weights(
                collection=self.mixed_collection,
                token=token,
                normalized=True,
            )
            ic_token_score = -np.sum(np.log2(np.reciprocal(attr_scores)))

            assert score == ic_token_score / collection_entropy

    def test_information_content_null_value_attribute(self):
        ic_scorer = InformationContentScoringHandler()
        collection_with_empty = generate_collection_with_token_traits(
            [
                {"bottom": "spec", "hat": "spec", "special": "true"},  # trait count = 3
                {"bottom": "1", "hat": "1", "special": "true"},  # trait count = 3
                {"bottom": "1", "hat": "1"},  # trait count = 2
                {"bottom": "2", "hat": "2"},  # trait count = 2
                {"bottom": "2", "hat": "2"},  # trait count = 2
                {"bottom": "3", "hat": "2"},  # trait count = 2
            ]
        )

        collection_entropy = ic_scorer._get_collection_entropy(collection_with_empty)
        collection_probs = []
        spread = {
            "bottom": {"1": 2, "2": 2, "3": 1, "spec": 1},
            "hat": {"1": 2, "2": 3, "spec": 1},
            "special": {"true": 2, "Null": 4},
            TRAIT_COUNT_ATTRIBUTE_NAME: {"2": 4, "3": 2},
        }
        for trait_dict in spread.values():
            for tokens_with_trait in trait_dict.values():
                collection_probs.append(tokens_with_trait / 6)

        expected_collection_entropy = -np.dot(
            collection_probs, np.log2(collection_probs)
        )
        assert np.round(collection_entropy, 10) == np.round(
            expected_collection_entropy, 10
        )

        scores = ic_scorer.score_tokens(
            collection=collection_with_empty, tokens=collection_with_empty.tokens
        )
        assert scores[0] > scores[1]
        assert scores[1] > scores[2]
        assert scores[5] > scores[2]
        assert scores[2] > scores[3]
        assert scores[3] == scores[4]

        for i, token in enumerate(collection_with_empty.tokens):
            attr_scores, _ = get_token_attributes_scores_and_weights(
                collection=collection_with_empty,
                token=token,
                normalized=False,
            )
            ic_token_score = -np.sum(np.log2(np.reciprocal(attr_scores)))
            expected_score = ic_token_score / collection_entropy

            assert np.round(scores[i], 10) == np.round(expected_score, 10)

    def test_information_content_empty_attribute(self):
        collection_with_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "2", "hat": "2"},
                {"bottom": "3", "hat": "2"},
            ]
        )

        collection_without_null = generate_collection_with_token_traits(
            [
                {"bottom": "1", "hat": "1", "special": "true"},
                {"bottom": "1", "hat": "1", "special": "none"},
                {"bottom": "2", "hat": "2", "special": "none"},
                {"bottom": "2", "hat": "2", "special": "none"},
                {"bottom": "3", "hat": "2", "special": "none"},
            ]
        )

        ic_scorer = InformationContentScoringHandler()

        scores_with_null = ic_scorer.score_tokens(
            collection=collection_with_null, tokens=collection_with_null.tokens
        )
        scores_without_null = ic_scorer.score_tokens(
            collection=collection_without_null,
            tokens=collection_without_null.tokens,
        )

        assert scores_with_null == scores_without_null

    @pytest.mark.skip(reason="Not including performance testing as required testing")
    def test_information_content_rarity_timing(self):
        ic_scorer = InformationContentScoringHandler()
        tic = time.time()
        ic_scorer.score_tokens(
            collection=self.mixed_collection,
            tokens=self.mixed_collection.tokens,
        )
        toc = time.time()
        assert (toc - tic) < self.max_scoring_time_for_10k_s
