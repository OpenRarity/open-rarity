"""Pinned 0.7.5 outputs for reviewing deliberate 1.0 behavior changes."""

import json
from pathlib import Path

import pytest

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.rarity_ranker import RarityRanker

FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "legacy_075.json").read_text()
)


@pytest.mark.parametrize("case", FIXTURES["cases"], ids=lambda case: case["name"])
def test_legacy_scores_and_ranks(case):
    collection = Collection(
        tokens=[
            Token.from_erc721("0xabc", token["id"], token["attributes"])
            for token in case["tokens"]
        ]
    )

    actual = RarityRanker.rank_collection(collection)
    assert len(actual) == len(case["expected"])
    for item, expected in zip(actual, case["expected"]):
        assert item.token.token_identifier.token_id == expected["id"]
        assert item.rank == expected["rank"]
        assert item.token_features.unique_attribute_count == expected["unique_traits"]
        assert item.score == pytest.approx(expected["score"], abs=1e-12, rel=0)
