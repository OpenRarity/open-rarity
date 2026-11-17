import json
from pathlib import Path

import pytest

from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import explain_collection, score_collection
from open_rarity.creator_config import parse_rarity_config

CASES = json.loads((Path(__file__).parent / "fixtures/conformance.json").read_text())[
    "cases"
]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_explanations_reconstruct_scores_without_changing_results(case):
    collection = parse_collection_json(json.dumps(case["collection"]))
    config = parse_rarity_config(case["config"])
    explained = explain_collection(collection, config)
    assert [row.result for row in explained] == score_collection(collection, config)
    by_id = {t.token_id: t for t in collection.tokens}
    for row in explained:
        assert sum(t.contribution for t in row.traits) == pytest.approx(
            row.result.score, abs=1e-12
        )
        assert sum(t.unique for t in row.traits) == row.result.unique_trait_count
        assert len(row.source_traits) == len(by_id[row.result.token_id].traits)
        assert row.normalization > 0
        for trait in row.traits:
            if trait.count is not None:
                assert trait.probability == trait.count / len(collection.tokens)
            if trait.mode == "exclude":
                assert trait.contribution == 0
                assert trait.count is None


def test_explanations_missing_numeric_and_duplicates():
    collection = parse_collection_json(
        '{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":"2"},{"trait_type":"Level","value":"1"},{"trait_type":"Hide","value":"x"}]},{"token_id":"2","traits":[{"trait_type":"Level","value":"bad"}]}]}'
    )
    config = parse_rarity_config(
        {
            "trait_count": "exclude",
            "traits": [
                {"trait_type": "Level", "mode": "higher_is_rarer"},
                {"trait_type": "Hide", "mode": "exclude"},
            ],
        }
    )
    rows = {r.result.token_id: r for r in explain_collection(collection, config)}
    level = next(t for t in rows["1"].traits if t.trait_type == "Level")
    assert (level.value, level.count, level.probability, level.information) == (
        "1",
        1,
        0.5,
        1,
    )
    assert [t.value for t in rows["1"].source_traits] == ["2", "1", "x"]
    invalid = next(t for t in rows["2"].traits if t.trait_type == "Level")
    assert (invalid.count, invalid.probability, invalid.information) == (None, None, 0)


def test_empty_explanation():
    assert explain_collection(parse_collection_json('{"tokens":[]}')) == []
