import json
from pathlib import Path

import pytest

from open_rarity.collection_input import CollectionInput, TokenInput, TraitInput
from open_rarity.collection_scorer import score_collection
from open_rarity.creator_config import RarityConfig


def test_legacy_fixture_compatibility():
    fixtures = json.loads(
        (Path(__file__).parent / "fixtures/legacy_075.json").read_text()
    )
    for case in fixtures["cases"]:
        collection = CollectionInput(
            tuple(
                TokenInput(
                    str(token["id"]),
                    tuple(TraitInput(k, v) for k, v in token["attributes"].items()),
                )
                for token in case["tokens"]
            )
        )
        for actual, expected in zip(score_collection(collection), case["expected"]):
            assert actual.token_id == str(expected["id"])
            assert actual.rank == expected["rank"]
            assert actual.score == pytest.approx(expected["score"], abs=1e-12, rel=0)
            assert actual.unique_trait_count == expected["unique_traits"]


def test_exact_numeric_order_and_missing_contribution():
    collection = CollectionInput(
        tuple(
            TokenInput(str(index), (TraitInput("Level", value),))
            for index, value in enumerate(
                ["9007199254740992", "9007199254740993", "invalid"]
            )
        )
    )
    results = score_collection(
        collection,
        RarityConfig(higher_is_rarer=frozenset({"Level"}), trait_count="exclude"),
    )
    assert [r.token_id for r in results] == ["1", "0", "2"]
    assert [r.rank for r in results] == [1, 2, 3]
    assert results[0].score == pytest.approx(1)
    assert results[-1].score == 0
    assert all(r.unique_trait_count == 0 for r in results)


def test_exclusions_duplicates_and_source_preservation():
    traits = (
        TraitInput("Hat", "Z"),
        TraitInput("Hat", "A"),
        TraitInput("Hat", " None "),
        TraitInput("Ignored", "rare"),
    )
    collection = CollectionInput(
        (TokenInput("2", traits), TokenInput("1", (TraitInput("Hat", "A"),)))
    )
    results = score_collection(
        collection, RarityConfig(excluded=frozenset({"Ignored"}))
    )
    assert [r.token_id for r in results] == ["1", "2"]
    assert all(r.score == 0 and r.rank == 1 for r in results)
    assert collection.tokens[0].traits == traits
