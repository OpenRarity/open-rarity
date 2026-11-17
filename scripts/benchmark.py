"""Reproducible local scorer benchmarks; build TypeScript before running."""

import argparse
import json
import platform
import statistics
import subprocess
import time

from open_rarity.collection_input import CollectionInput, TokenInput, TraitInput
from open_rarity.collection_scorer import score_collection
from open_rarity.creator_config import RarityConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10000, 100000])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1 or any(n < 1 for n in args.sizes):
        parser.error("sizes and repeats must be positive")
    for size in args.sizes:
        for mode in ("categorical", "configured"):
            collection = CollectionInput(
                tuple(
                    TokenInput(
                        str(i),
                        tuple(
                            TraitInput(f"Trait{j}", str((i * (j + 1)) % (17 + j)))
                            for j in range(8)
                        ),
                    )
                    for i in range(size)
                )
            )
            config = (
                None
                if mode == "categorical"
                else RarityConfig(higher_is_rarer=frozenset({"Trait0"}))
            )
            score_collection(CollectionInput(collection.tokens[:100]), config)
            timings = []
            for _ in range(args.repeats):
                start = time.perf_counter()
                results = score_collection(collection, config)
                timings.append(time.perf_counter() - start)
                assert len(results) == size
            python_row = {
                "runtime": "python",
                "version": platform.python_version(),
                "tokens": size,
                "traits_per_token": 8,
                "mode": mode,
                "seconds": timings,
                "median_seconds": statistics.median(timings),
            }
            print(json.dumps(python_row), flush=True)
    output = subprocess.check_output(
        ["node", "scripts/benchmark.mjs", json.dumps(args.sizes), str(args.repeats)],
        text=True,
    )
    print(output, end="")


if __name__ == "__main__":
    main()
