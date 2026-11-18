"""Build and install actual artifacts in isolated consumers. Never publishes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT, **kwargs):
    return subprocess.run(args, cwd=cwd, check=True, **kwargs)


def main():
    python_version = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"][
        "poetry"
    ]["version"]
    npm_version = json.loads((ROOT / "typescript/package.json").read_text())["version"]
    normalized = python_version.replace(".dev", "-dev.").replace("rc", "-rc.")
    if normalized != npm_version:
        raise SystemExit(
            f"Package versions do not match: {python_version}, {npm_version}"
        )
    with tempfile.TemporaryDirectory(prefix="openrarity-dist-") as directory:
        temp = Path(directory)
        artifacts = temp / "artifacts"
        run(sys.executable, "-m", "build", "--outdir", str(artifacts))
        wheel = next(artifacts.glob("*.whl"))
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            for name in (
                "open_rarity/py.typed",
                "open_rarity/cli.py",
                "open_rarity/collection_scorer.py",
            ):
                assert name in names, name
            assert any(name.endswith("LICENSE") for name in names)
        # Building the wheel from the sdist also checks that source packaging is complete.
        run(
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            str(next(artifacts.glob("*.tar.gz"))),
            "--wheel-dir",
            str(temp / "rebuilt"),
        )
        run(sys.executable, "-m", "venv", str(temp / "venv"))
        python = str(temp / "venv/bin/python")
        run(python, "-m", "pip", "install", str(wheel), cwd=temp)
        smoke = 'from open_rarity.collection_input import parse_collection_json; from open_rarity.collection_scorer import explain_collection; c=parse_collection_json(\'{"tokens":[{"token_id":"1","traits":[]}]}\'); assert explain_collection(c)[0].result.rank == 1'
        run(python, "-I", "-c", smoke, cwd=temp)
        for executable in (
            [python, "-I", "-m", "open_rarity"],
            [str(temp / "venv/bin/openrarity")],
        ):
            result = run(
                *executable,
                "-",
                cwd=temp,
                input='{"tokens":[]}',
                text=True,
                capture_output=True,
            )
            assert json.loads(result.stdout) == []
        packed = run(
            "npm",
            "pack",
            "--json",
            "--pack-destination",
            str(temp),
            cwd=ROOT / "typescript",
            capture_output=True,
            text=True,
        )
        package = json.loads(packed.stdout)[0]
        files = {entry["path"] for entry in package["files"]}
        assert {"LICENSE", "README.md", "dist/index.js", "dist/index.d.ts"} <= files
        assert not any(name.startswith(("test/", "node_modules/")) for name in files)
        consumer = temp / "consumer"
        consumer.mkdir()
        run(
            "npm",
            "install",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            "--prefix",
            str(consumer),
            str(temp / package["filename"]),
            cwd=consumer,
        )
        (consumer / "smoke.mts").write_text(
            'import {explainCollection, type ExplainedToken} from "open-rarity";\n'
            'import {fetchOpenSeaCollection} from "open-rarity/opensea";\n'
            'import type {OpenSeaCollectionOptions} from "open-rarity/opensea";\n'
            "const fetcher: (slug: string, options: OpenSeaCollectionOptions) => Promise<unknown> = fetchOpenSeaCollection;\n"
            "const rows: ExplainedToken[] = explainCollection({tokens: []});\n"
        )
        run(
            "node",
            str(ROOT / "typescript/node_modules/typescript/bin/tsc"),
            "--noEmit",
            "--strict",
            "--module",
            "nodenext",
            "--target",
            "es2022",
            "smoke.mts",
            cwd=consumer,
        )
        run(
            "node",
            "--input-type=module",
            "-e",
            """
            import { fetchOpenSeaCollection } from "open-rarity/opensea";
            import { scoreCollection, explainCollection, parseCollectionJson } from "open-rarity";
            if (typeof fetchOpenSeaCollection !== "function") throw Error("Missing OpenSea export");
            const collection = parseCollectionJson('{"tokens":[{"token_id":"1","traits":[]}]}');
            if (scoreCollection(collection)[0].rank !== 1 || explainCollection(collection)[0].result.rank !== 1)
              throw Error("Package smoke failed");
            """,
            cwd=consumer,
        )
    print(
        "Python wheel, rebuilt sdist, console command, and npm tarball installation passed"
    )


if __name__ == "__main__":
    main()
