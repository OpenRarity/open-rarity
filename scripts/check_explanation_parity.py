"""Compare complete explanation trees across runtimes and shared fixtures."""

from dataclasses import asdict
import json
import math
from pathlib import Path
import subprocess

from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import explain_collection
from open_rarity.creator_config import parse_rarity_config


def compare(a, b, path="root"):
    if isinstance(a, float):
        assert isinstance(b, (int, float)) and math.isclose(
            a, b, rel_tol=0, abs_tol=1e-12
        ), (path, a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys(), path
        for key in a:
            compare(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (left, right) in enumerate(zip(a, b)):
            compare(left, right, f"{path}[{i}]")
    else:
        assert a == b, (path, a, b)


def main():
    cases = json.loads(Path("tests/fixtures/conformance.json").read_text())["cases"]
    cases += [
        {
            "collection": {
                "tokens": [
                    {
                        "token_id": "1",
                        "traits": [{"trait_type": "Hat", "value": "none"}],
                    },
                    {"token_id": "2", "traits": []},
                    {
                        "token_id": "3",
                        "traits": [{"trait_type": "Hat", "value": "Cap"}],
                    },
                ]
            },
            "config": {},
        },
        {"collection": {"tokens": []}, "config": {}},
    ]
    for legacy in json.loads(Path("tests/fixtures/legacy_075.json").read_text())[
        "cases"
    ]:
        cases.append(
            {
                "collection": {
                    "tokens": [
                        {
                            "token_id": str(t["id"]),
                            "traits": [
                                {"trait_type": k, "value": v}
                                for k, v in t["attributes"].items()
                            ],
                        }
                        for t in legacy["tokens"]
                    ]
                },
                "config": {},
            }
        )
    inputs = [
        {"source": json.dumps(c["collection"]), "config": c["config"]} for c in cases
    ]
    js = "import {parseCollectionJson,explainCollection} from './typescript/dist/index.js';let t='';for await(const c of process.stdin)t+=c;console.log(JSON.stringify(JSON.parse(t).map(c=>explainCollection(parseCollectionJson(c.source),c.config))));"
    actual = json.loads(
        subprocess.check_output(
            ["node", "--input-type=module", "-e", js],
            input=json.dumps(inputs),
            text=True,
        )
    )
    assert len(actual) == len(inputs)
    for case, result in zip(inputs, actual):
        expected = [
            asdict(r)
            for r in explain_collection(
                parse_collection_json(case["source"]),
                parse_rarity_config(case["config"]),
            )
        ]
        compare(expected, result)
    print(f"{len(cases)} complete explanation trees match across Python and TypeScript")


if __name__ == "__main__":
    main()
