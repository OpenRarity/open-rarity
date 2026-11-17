# Scoring benchmarks

Run from an installed checkout after `npm ci --prefix typescript` and
`npm run build --prefix typescript`:

```sh
python -m scripts.benchmark --sizes 10000 100000 --repeats 3
```

Each runtime scores deterministic collections with eight traits per token. The
categorical case uses compatibility scoring; the configured case makes one trait
higher-is-rarer. A 100-token warmup precedes three measured runs. Timings cover
scoring and ranking, excluding data generation, JSON parsing, and process startup.

Local baseline on macOS arm64, 2026-11-17, Python 3.14.5 and Node 26.12.1:

| Tokens | Python categorical | Python configured | Node categorical | Node configured |
| --- | --- | --- | --- | --- |
| 10,000 | 0.236 s | 0.221 s | 0.033 s | 0.029 s |
| 100,000 | 3.084 s | 2.359 s | 0.228 s | 0.340 s |

Values are medians, not performance guarantees. The dataset has repeated values
and short decimal strings; high-cardinality traits, long numbers, explanation
output, memory use, and fetching need separate measurements. Benchmark JSON lines
include every sample and runtime version. CI checks correctness without timing
thresholds, since shared-runner load varies.
