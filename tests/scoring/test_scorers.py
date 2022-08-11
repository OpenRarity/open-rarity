from open_rarity.scoring.scorers.geometric_mean_scorer import (
    GeometricMeanRarityScorer,
)
from open_rarity.scoring.scorers.arithmetic_mean_scorer import (
    ArithmeticMeanRarityScorer,
)
from open_rarity.scoring.scorers.harmonic_mean_scorer import (
    HarmonicMeanRarityScorer,
)
from open_rarity.scoring.scorers.information_content_scorer import (
    InformationContentRarityScorer,
)
from tests.utils import (
    generate_uniform_rarity_collection,
    generate_onerare_rarity_collection,
    generate_collection_with_token_traits,
)
import numpy as np
from random import shuffle

def generate_mixed_collection(max_total_supply: int = 10000):
    if max_total_supply % 10 != 0 or max_total_supply < 100:
        raise Exception("only multiples of 10 and greater than 100 please.")

    # "hat": 20% have "cap", 30% have "beanie", 45% have "hood", 5% have "visor"
    # "shirt": 80% have "white-t", 20% have "vest"
    # "special": 1% have "special" others none
    token_ids = list(range(max_total_supply))
    shuffle(token_ids)
    hat_spread = [
        ["cap", int(max_total_supply * .2)],
        ["beanie", int(max_total_supply * .3)],
        ["hood", int(max_total_supply * .45)],
        ["visor", int(max_total_supply * .5)]
    ]
    shirt_spread = [
        ["white-t", int(max_total_supply * .8)],
        ["vest", int(max_total_supply * .2)]
    ]
    special_spread = [
        ["special", int(max_total_supply * .1)],
        ["not_special", int(max_total_supply * .9)]
    ]

    def get_trait_value(trait_spread, idx):
        trait_value_idx = 0
        max_idx_for_trait_value = trait_spread[trait_value_idx][1]
        while idx >= max_idx_for_trait_value:
            trait_value_idx += 1
            max_idx_for_trait_value += trait_spread[trait_value_idx][1]
        return trait_spread[trait_value_idx][0]

    token_ids_to_traits = {}
    for idx, token_id in enumerate(token_ids):
        traits = {
            "hat": get_trait_value(hat_spread, idx),
            "shirt": get_trait_value(shirt_spread, idx),
            "special": get_trait_value(special_spread, idx),
        }

        token_ids_to_traits[token_id] = traits

    return generate_collection_with_token_traits(
        [token_ids_to_traits[token_id] for token_id in range(max_total_supply)]
    )



class TestScoring:

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

    mixed_collection = generate_mixed_collection()


    def test_geometric_mean_scorer_uniform(self) -> None:
        """test the geometric mean implementation of score_token"""
        geometric_mean_rarity = GeometricMeanRarityScorer()
        uniform_tokens_to_test = [
            self.uniform_collection.tokens[0],
            self.uniform_collection.tokens[1405],
            self.uniform_collection.tokens[9999],
        ]
        expected_uniform_score = 10.0
        for token_to_test in uniform_tokens_to_test:
            assert np.round(
                geometric_mean_rarity.score_token(
                    collection=self.uniform_collection, token=token_to_test
                ),
                12,
            ) == np.round(expected_uniform_score, 12)

    def test_geometric_mean_scorer_onerare(self) -> None:
        geometric_mean_rarity = GeometricMeanRarityScorer()
        common_token = self.onerare_collection.tokens[0]
        # Since weights and scores for every trait will all be the same,
        # the score is just the same as a trait score
        expected_common_score = 10000 / 1111
        assert np.round(
            geometric_mean_rarity.score_token(
                collection=self.onerare_collection, token=common_token
            ), 8
        ) == np.round(expected_common_score, 8)

        rare_token = self.onerare_collection.tokens[-1]
        # Since weights and scores for every trait will all be the same,
        # the score is just the same as a trait score
        expected_rare_score = 10000
        assert np.round(
            geometric_mean_rarity.score_token(
                collection=self.onerare_collection, token=rare_token
            ), 8
        ) == np.round(expected_rare_score, 8)

    def test_arithmetic_mean(self) -> None:
        """test the arithmetic mean implementation of score_token"""

        arithmetic_mean_rarity = ArithmeticMeanRarityScorer()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_arithmetic_mean = 10

        assert np.round(
            arithmetic_mean_rarity.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_arithmetic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[0]
        # onerare_arithmetic_mean = 9.80018002
        # assert np.round(
        #     arithmetic_mean_rarity.score_token(
        #       collection=self.onerare_collection, token=onerare_token_to_test
        #       ), 8
        # ) == np.round(onerare_arithmetic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[-1]
        # onerare_arithmetic_mean = 2008.0
        # assert np.round(
        #     arithmetic_mean_rarity.score_token(
        #           collection=self.onerare_collection, token=onerare_token_to_test
        #       ), 8
        # ) == np.round(onerare_arithmetic_mean, 8)

    def test_harmonic_mean(self) -> None:
        """test the harmonic mean implementation of score_token"""

        harmonic_mean_rarity = HarmonicMeanRarityScorer()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_harmonic_mean = 10
        assert np.round(
            harmonic_mean_rarity.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_harmonic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[0]
        # onerare_harmonic_mean = 9.78282137
        # assert np.round(
        #     harmonic_mean_rarity.score_token(
        #           collection=self.onerare_collection, token=onerare_token_to_test
        #       ), 8
        # ) == np.round(onerare_harmonic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[-1]
        # onerare_harmonic_mean = 12.49687578

        # assert np.round(
        #     harmonic_mean_rarity.score_token(
        #       collection=self.onerare_collection, token=onerare_token_to_test
        #       ), 8
        # ) == np.round(onerare_harmonic_mean, 8)

    def test_information_content_rarity(self):
        information_content_rarity = InformationContentRarityScorer()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_ic_rarity = 1.0
        assert np.round(
            information_content_rarity.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_ic_rarity, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[0]
        # onerare_ic_mean = 0.99085719
        # assert np.round(
        #     information_content_rarity.score_token(
        #       collection=self.onerare_collection, token=onerare_token_to_test),
        #     8,
        # ) == np.round(onerare_ic_mean, 8)
