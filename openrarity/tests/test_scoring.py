from openrarity.scoring.geometric_mean import GeometricMeanRarity
from openrarity.scoring.arithmetic_mean import ArithmeticMeanRarity
from openrarity.scoring.harmonic_mean import HarmonicMeanRarity
from openrarity.tests.utils import (
    generate_uniform_rarity_collection,
    generate_onerare_rarity_collection,
)
import numpy as np


def test_geometric_mean(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> None:
    """test the geometric mean implementation of score_token"""

    geometric_mean_rarity = GeometricMeanRarity()

    uniform_collection = generate_uniform_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    uniform_token_to_test = uniform_collection.tokens[0]
    # set collection manually as a workaround for circular import
    uniform_token_to_test.collection = uniform_collection
    uniform_geometric_mean = np.prod(
        [1 / values_per_attribute] * attribute_count
    ) ** (1 / attribute_count)
    assert (
        geometric_mean_rarity.score_token(uniform_token_to_test)
        == uniform_geometric_mean
    )

    onerare_collection = generate_onerare_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    onerare_token_to_test = onerare_collection.tokens[
        0
    ]  # test the common token
    onerare_token_to_test.collection = onerare_collection
    onerare_geometric_mean = np.prod(
        [(token_total_supply / values_per_attribute) / token_total_supply]
        * (attribute_count - 1)
        + [
            ((token_total_supply - 1) / (values_per_attribute - 1))
            / token_total_supply
        ]
    ) ** (1 / attribute_count)
    assert (
        geometric_mean_rarity.score_token(onerare_token_to_test)
        == onerare_geometric_mean
    )

    onerare_token_to_test = onerare_collection.tokens[
        -1
    ]  # test the rare token
    onerare_token_to_test.collection = onerare_collection
    onerare_geometric_mean = np.prod(
        [(token_total_supply / values_per_attribute) / token_total_supply]
        * (attribute_count - 1)
        + [1 / token_total_supply]
    ) ** (1 / attribute_count)
    assert (
        geometric_mean_rarity.score_token(onerare_token_to_test)
        == onerare_geometric_mean
    )


def test_arithmetic_mean(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> None:
    """test the arithmetic mean implementation of score_token"""

    arithmetic_mean_rarity = ArithmeticMeanRarity()

    uniform_collection = generate_uniform_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    uniform_token_to_test = uniform_collection.tokens[0]
    uniform_token_to_test.collection = uniform_collection
    uniform_arithmetic_mean = np.mean(
        [1 / values_per_attribute] * attribute_count
    )
    assert (
        arithmetic_mean_rarity.score_token(uniform_token_to_test)
        == uniform_arithmetic_mean
    )

    onerare_collection = generate_onerare_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    onerare_token_to_test = onerare_collection.tokens[0]
    onerare_token_to_test.collection = onerare_collection
    onerare_arithmetic_mean = np.mean(
        [(token_total_supply / values_per_attribute) / token_total_supply]
        * (attribute_count - 1)
        + [
            ((token_total_supply - 1) / (values_per_attribute - 1))
            / token_total_supply
        ]
    )
    assert (
        arithmetic_mean_rarity.score_token(onerare_token_to_test)
        == onerare_arithmetic_mean
    )

    onerare_token_to_test = onerare_collection.tokens[-1]
    onerare_token_to_test.collection = onerare_collection
    onerare_arithmetic_mean = np.mean(
        [(token_total_supply / values_per_attribute) / token_total_supply]
        * (attribute_count - 1)
        + [1 / token_total_supply]
    )
    assert (
        arithmetic_mean_rarity.score_token(onerare_token_to_test)
        == onerare_arithmetic_mean
    )


def test_harmonic_mean(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> None:
    """test the harmonic mean implementation of score_token"""

    harmonic_mean_rarity = HarmonicMeanRarity()

    uniform_collection = generate_uniform_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    uniform_token_to_test = uniform_collection.tokens[0]
    uniform_token_to_test.collection = uniform_collection
    uniform_harmonic_mean = (
        np.mean(np.reciprocal([1 / values_per_attribute] * attribute_count))
        ** -1
    )
    assert (
        harmonic_mean_rarity.score_token(uniform_token_to_test)
        == uniform_harmonic_mean
    )

    onerare_collection = generate_onerare_rarity_collection(
        attribute_count, values_per_attribute, token_total_supply
    )

    onerare_token_to_test = onerare_collection.tokens[0]
    onerare_token_to_test.collection = onerare_collection
    onerare_harmonic_mean = (
        np.mean(
            np.reciprocal(
                [
                    (token_total_supply / values_per_attribute)
                    / token_total_supply
                ]
                * (attribute_count - 1)
                + [
                    ((token_total_supply - 1) / (values_per_attribute - 1))
                    / token_total_supply
                ]
            )
        )
        ** -1
    )
    assert (
        harmonic_mean_rarity.score_token(onerare_token_to_test)
        == onerare_harmonic_mean
    )

    onerare_token_to_test = onerare_collection.tokens[-1]
    onerare_token_to_test.collection = onerare_collection
    onerare_harmonic_mean = (
        np.mean(
            np.reciprocal(
                [
                    (token_total_supply / values_per_attribute)
                    / token_total_supply
                ]
                * (attribute_count - 1)
                + [1 / token_total_supply]
            )
        )
        ** -1
    )
    assert (
        harmonic_mean_rarity.score_token(onerare_token_to_test)
        == onerare_harmonic_mean
    )
