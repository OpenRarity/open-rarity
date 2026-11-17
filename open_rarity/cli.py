"""Score local collection JSON without fetching metadata."""

import argparse
import csv
from dataclasses import asdict
import io
import json
from pathlib import Path
import sys

from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import explain_collection, score_collection
from open_rarity.creator_config import parse_rarity_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Collection JSON path, or - for stdin")
    parser.add_argument("-o", "--output", help="Output path (default: stdout)")
    parser.add_argument(
        "--config", help="Creator settings JSON; overrides embedded rarity"
    )
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument(
        "--explain", action="store_true", help="Include per-trait details in JSON"
    )
    args = parser.parse_args()
    if args.explain and args.format != "json":
        parser.error("--explain requires --format json")
    try:
        source = (
            sys.stdin.read()
            if args.input == "-"
            else Path(args.input).read_text(encoding="utf-8")
        )
        collection = parse_collection_json(source)
        config_source = (
            Path(args.config).read_text(encoding="utf-8") if args.config else source
        )
        config = parse_rarity_config(json.loads(config_source))
        scorer = explain_collection if args.explain else score_collection
        rows = [asdict(row) for row in scorer(collection, config)]
        if args.format == "json":
            output = (
                json.dumps(rows, ensure_ascii=True, allow_nan=False, indent=2) + "\n"
            )
        else:
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(
                stream, fieldnames=["token_id", "score", "rank", "unique_trait_count"]
            )
            writer.writeheader()
            writer.writerows(rows)
            output = stream.getvalue()
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"openrarity: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
