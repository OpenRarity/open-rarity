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
from tests.test_utils import (
    generate_uniform_rarity_collection,
    generate_onerare_rarity_collection,
)
import numpy as np


class TestScoring:

    uniform_collection = generate_uniform_rarity_collection(
        attribute_count=5,
        values_per_attribute=10,
        token_total_supply=10000,
    )

    onerare_collection = generate_onerare_rarity_collection(
        attribute_count=5,
        values_per_attribute=10,
        token_total_supply=10000,
    )

    # NOTE: All the previous unit tests verifying one rarity collections were wrong
    # because since the helper method wasn't actually calling the correct one rarity probability helper method.
    # TODO [dan, vicky]: To add replacement tests for rarity ones later.

    def test_geometric_mean_scorer(self) -> None:
        """test the geometric mean implementation of score_token"""

        geometric_mean_rarity = GeometricMeanRarityScorer()

        uniform_token_to_test = self.uniform_collection.tokens[0]
        uniform_geometric_mean = 10.0
        assert np.round(
            geometric_mean_rarity.score_token(
                collection=self.uniform_collection, token=uniform_token_to_test
            ),
            8,
        ) == np.round(uniform_geometric_mean, 8)

        onerare_token_to_test = self.onerare_collection.tokens[
            0
        ]  # test the common token
        onerare_geometric_mean = 9.79167947
        assert np.round(
            geometric_mean_rarity.score_token(
                collection=self.onerare_collection, token=onerare_token_to_test
            ),
            8,
        ) == np.round(onerare_geometric_mean, 8)

        onerare_token_to_test = self.onerare_collection.tokens[
            -1
        ]  # test the rare token
        # onerare_geometric_mean = 39.81071706
        # assert np.round(
        #     geometric_mean_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test), 8
        # ) == np.round(onerare_geometric_mean, 8)

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
        #     arithmetic_mean_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test), 8
        # ) == np.round(onerare_arithmetic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[-1]
        # onerare_arithmetic_mean = 2008.0
        # assert np.round(
        #     arithmetic_mean_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test), 8
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
        #     harmonic_mean_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test), 8
        # ) == np.round(onerare_harmonic_mean, 8)

        # onerare_token_to_test = self.onerare_collection.tokens[-1]
        # onerare_harmonic_mean = 12.49687578

        # assert np.round(
        #     harmonic_mean_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test), 8
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
        #     information_content_rarity.score_token(collection=self.onerare_collection, token=onerare_token_to_test),
        #     8,
        # ) == np.round(onerare_ic_mean, 8)
