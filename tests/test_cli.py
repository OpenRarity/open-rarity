import csv
import io
import json
import subprocess
import sys

SOURCE = '{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":9007199254740992}]},{"token_id":"2","traits":[{"trait_type":"Level","value":9007199254740993}]}],"rarity":{"trait_count":"exclude","traits":[{"trait_type":"Level","mode":"higher_is_rarer"}]}}'


def run(*args, source=SOURCE):
    return subprocess.run(
        [sys.executable, "-m", "open_rarity", *args],
        input=source,
        text=True,
        capture_output=True,
    )


def test_stdin_exact_scores_and_explanations():
    result = run("-", "--explain")
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert rows[0]["result"]["token_id"] == "2"
    assert rows[0]["result"]["score"] == 1
    assert rows[0]["source_traits"][0]["value"] == "9007199254740993"


def test_file_csv_and_override(tmp_path):
    source, output, config = [
        tmp_path / name for name in ("input.json", "output.csv", "config.json")
    ]
    source.write_text(SOURCE)
    config.write_text(
        '{"trait_count":"exclude","traits":[{"trait_type":"Level","mode":"exclude"}]}'
    )
    result = run(
        str(source), "-o", str(output), "--format", "csv", "--config", str(config)
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    rows = list(csv.DictReader(io.StringIO(output.read_text())))
    assert [r["token_id"] for r in rows] == ["1", "2"]
    assert [float(r["score"]) for r in rows] == [0, 0]


def test_invalid_input_leaves_output_untouched(tmp_path):
    output = tmp_path / "result.json"
    output.write_text("keep")
    for source in (
        "{",
        '{"tokens":[{"traits":[]}]}',
        '{"tokens":[{"token_id":"x","traits":[]}]}',
    ):
        result = run("-", "-o", str(output), source=source)
        assert result.returncode == 2
        assert "Traceback" not in result.stderr
        assert output.read_text() == "keep"
    assert run("-", "--explain", "--format", "csv").returncode == 2
