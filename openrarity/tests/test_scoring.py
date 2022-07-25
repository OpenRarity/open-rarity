from openrarity.scoring.geometric_mean import GeometricMeanRarity
from openrarity.scoring.arithmetic_mean import ArithmeticMeanRarity
from openrarity.scoring.harmonic_mean import HarmonicMeanRarity
from openrarity.tests.test_utils import (
    generate_uniform_rarity_collection,
    generate_onerare_rarity_collection,
)
import numpy as np


class TestScorring:
    def test_geometric_mean(self) -> None:
        """test the geometric mean implementation of score_token"""

        geometric_mean_rarity = GeometricMeanRarity()

        uniform_collection = generate_uniform_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        uniform_token_to_test = uniform_collection.tokens[0]
        # set collection manually as a workaround for circular import
        uniform_token_to_test.collection = uniform_collection
        uniform_geometric_mean = 10.0
        assert np.round(
            geometric_mean_rarity.score_token(uniform_token_to_test), 8
        ) == np.round(uniform_geometric_mean, 8)

        onerare_collection = generate_onerare_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        onerare_token_to_test = onerare_collection.tokens[
            0
        ]  # test the common token
        onerare_token_to_test.collection = onerare_collection
        onerare_geometric_mean = 9.79167947
        assert np.round(
            geometric_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_geometric_mean, 8)

        onerare_token_to_test = onerare_collection.tokens[
            -1
        ]  # test the rare token
        onerare_token_to_test.collection = onerare_collection
        onerare_geometric_mean = 39.81071706
        assert np.round(
            geometric_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_geometric_mean, 8)

    def test_arithmetic_mean(self) -> None:
        """test the arithmetic mean implementation of score_token"""

        arithmetic_mean_rarity = ArithmeticMeanRarity()

        uniform_collection = generate_uniform_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        uniform_token_to_test = uniform_collection.tokens[0]
        uniform_token_to_test.collection = uniform_collection
        uniform_arithmetic_mean = 10
        assert np.round(
            arithmetic_mean_rarity.score_token(uniform_token_to_test), 8
        ) == np.round(uniform_arithmetic_mean, 8)

        onerare_collection = generate_onerare_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        onerare_token_to_test = onerare_collection.tokens[0]
        onerare_token_to_test.collection = onerare_collection
        onerare_arithmetic_mean = 9.80018002
        assert np.round(
            arithmetic_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_arithmetic_mean, 8)

        onerare_token_to_test = onerare_collection.tokens[-1]
        onerare_token_to_test.collection = onerare_collection
        onerare_arithmetic_mean = 2008.0
        assert np.round(
            arithmetic_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_arithmetic_mean, 8)

    def test_harmonic_mean(self) -> None:
        """test the harmonic mean implementation of score_token"""

        harmonic_mean_rarity = HarmonicMeanRarity()

        uniform_collection = generate_uniform_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        uniform_token_to_test = uniform_collection.tokens[0]
        uniform_token_to_test.collection = uniform_collection
        uniform_harmonic_mean = 10
        assert np.round(
            harmonic_mean_rarity.score_token(uniform_token_to_test), 8
        ) == np.round(uniform_harmonic_mean, 8)

        onerare_collection = generate_onerare_rarity_collection(
            attribute_count=5,
            values_per_attribute=10,
            token_total_supply=10000,
        )

        onerare_token_to_test = onerare_collection.tokens[0]
        onerare_token_to_test.collection = onerare_collection
        onerare_harmonic_mean = 9.78282137
        assert np.round(
            harmonic_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_harmonic_mean, 8)

        onerare_token_to_test = onerare_collection.tokens[-1]
        onerare_token_to_test.collection = onerare_collection
        onerare_harmonic_mean = 12.49687578

        assert np.round(
            harmonic_mean_rarity.score_token(onerare_token_to_test), 8
        ) == np.round(onerare_harmonic_mean, 8)
