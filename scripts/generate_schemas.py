"""Generate structural JSON Schemas from the scoring dataclasses."""

import argparse
import json
from pathlib import Path

from pydantic import TypeAdapter

from open_rarity.collection_input import CollectionInput
from open_rarity.collection_scorer import TokenRarityResult

ROOT = Path(__file__).resolve().parents[1]


def schemas() -> dict[str, dict]:
    collection = TypeAdapter(CollectionInput).json_schema(mode="validation")
    # JSON parsers require an explicit traits array, even though typed callers
    # can use the TokenInput default.
    required = collection["$defs"]["TokenInput"].setdefault("required", [])
    if "traits" not in required:
        required.append("traits")
    return {
        "collection": collection,
        "results": TypeAdapter(list[TokenRarityResult]).json_schema(
            mode="serialization"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, schema in schemas().items():
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["description"] = (
            "OpenRarity 1.0 development structural schema. "
            "Scoring performs additional semantic validation; see docs/api.md."
        )
        target = ROOT / "schemas" / f"{name}.schema.json"
        content = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not target.exists() or target.read_text() != content:
                raise SystemExit(f"Stale schema: {target.relative_to(ROOT)}")
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_text(content)


if __name__ == "__main__":
    main()
