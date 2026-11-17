import json
from pathlib import Path

import pytest

from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import score_collection
from open_rarity.creator_config import parse_rarity_config

CASES = json.loads((Path(__file__).parent / "fixtures/conformance.json").read_text())[
    "cases"
]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_shared_conformance(case):
    result = score_collection(
        parse_collection_json(json.dumps(case["collection"])),
        parse_rarity_config(case["config"]),
    )
    assert len(result) == len(case["expected"])
    for actual, expected in zip(result, case["expected"]):
        assert actual.token_id == expected["token_id"]
        assert actual.rank == expected["rank"]
        assert actual.unique_trait_count == expected["unique_trait_count"]
        assert actual.score == pytest.approx(expected["score"], abs=1e-12, rel=0)


def test_exact_json_decimal_comparison():
    source = '{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":0.100000000000000001}]},{"token_id":"2","traits":[{"trait_type":"Level","value":0.100000000000000002}]}]}'
    results = score_collection(
        parse_collection_json(source),
        parse_rarity_config(
            {
                "trait_count": "exclude",
                "traits": [{"trait_type": "Level", "mode": "higher_is_rarer"}],
            }
        ),
    )
    assert [r.token_id for r in results] == ["2", "1"]
    assert [r.score for r in results] == [1, 0]
