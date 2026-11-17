"""Deterministic cross-runtime regression check; build TypeScript first."""

import random
import json
import subprocess
import math
from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import score_collection
from open_rarity.creator_config import parse_rarity_config

r = random.Random(42)
cases = []
for i in range(200):
    config = r.choice(
        [
            {},
            {"trait_count": "exclude"},
            {"traits": [{"trait_type": "Level", "mode": "higher_is_rarer"}]},
            {
                "trait_count": "higher_is_rarer",
                "traits": [{"trait_type": "Hat", "mode": "exclude"}],
            },
        ]
    )
    tokens = []
    for t in range(r.randrange(1, 15)):
        traits = [
            {
                "trait_type": r.choice(["Hat", "Level", "😀", "\ue000"]),
                "value": r.choice(["A", "B", "none", "", None, 7, 8, -3, "1e2", "1.0"]),
            }
            for _ in range(r.randrange(5))
        ]
        tokens.append({"token_id": str(t), "traits": traits})
    cases.append({"source": json.dumps({"tokens": tokens}), "config": config})
js = "import {parseCollectionJson,scoreCollection} from './typescript/dist/index.js';let t='';for await(const c of process.stdin)t+=c;console.log(JSON.stringify(JSON.parse(t).map(c=>scoreCollection(parseCollectionJson(c.source),c.config))));"
actual = json.loads(
    subprocess.check_output(
        ["node", "--input-type=module", "-e", js], input=json.dumps(cases), text=True
    )
)
for i, (case, rows) in enumerate(zip(cases, actual)):
    expected = score_collection(
        parse_collection_json(case["source"]), parse_rarity_config(case["config"])
    )
    for a, b in zip(rows, expected):
        assert (a["token_id"], a["rank"], a["unique_trait_count"]) == (
            b.token_id,
            b.rank,
            b.unique_trait_count,
        ), (i, case, rows, expected)
        assert math.isclose(a["score"], b.score, rel_tol=0, abs_tol=1e-12)
print("200 deterministic randomized cross-language cases passed")
