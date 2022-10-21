import time
from random import sample

import numpy as np
import pytest

from openrarity.scorers.information_content import IC
from openrarity.scorers.utils import get_token_attributes_scores_and_weights
from tests.helpers import (
    generate_collection_with_token_traits,
    generate_mixed_collection,
    generate_onerare_rarity_collection,
    generate_uniform_rarity_collection,
    get_mixed_trait_spread,
)


class TestScoringHandlers:
    max_scoring_time_for_10k_s = 2

    uniform_collection = generate_uniform_rarity_collection(
        attribute_count=5,
        values_per_attribute=10,
        token_total_supply=10000,
    )

    # The last token (#9999) has a unique attribute value for all
    # 5 different attribute types
    onerare_collection = generate_onerare_rarity_collection(
        attribute_count=5,
        values_per_attribute=10,
        token_total_supply=10000,
    )

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
        information_content_rarity = IC()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_ic_rarity = 1.0
        assert np.round(
            information_content_rarity.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_ic_rarity, 8)

    def test_information_content_rarity_mixed(self):
        ic_scorer = IC()

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

    def test_information_content_null_attribute(self):
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
                {"bottom": "1", "hat": "1", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "2", "hat": "2", "special": "false"},
                {"bottom": "3", "hat": "2", "special": "false"},
            ]
        )

        ic_scorer = IC()

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
        ic_scorer = IC()
        tic = time.time()
        ic_scorer.score_tokens(
            collection=self.mixed_collection,
            tokens=self.mixed_collection.tokens,
        )
        toc = time.time()
        assert (toc - tic) < self.max_scoring_time_for_10k_s
