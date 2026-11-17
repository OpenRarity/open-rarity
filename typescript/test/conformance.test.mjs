import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  scoreCollection,
  parseCollectionJson,
  parseCreatorRarityConfig,
} from "../dist/index.js";
// Parse each collection directly from JSON so large integers never pass through Number.
const text = readFileSync(
  new URL("../../tests/fixtures/conformance.json", import.meta.url),
  "utf8",
);
const fixtures = JSON.parse(text, (key, value, context) =>
  typeof value === "number" && key === "value"
    ? { decimalSource: context.source }
    : value,
);
for (const c of fixtures.cases)
  test(c.name, () => {
    const json = JSON.stringify(c.collection).replace(
      /\{"decimalSource":"([^"]+)"\}/g,
      "$1",
    );
    const actual = scoreCollection(
      parseCollectionJson(json),
      parseCreatorRarityConfig(c.config),
    );
    assert.equal(actual.length, c.expected.length);
    for (let i = 0; i < actual.length; i++) {
      const a = actual[i],
        e = c.expected[i];
      assert.equal(a.token_id, e.token_id);
      assert.equal(a.rank, e.rank);
      assert.equal(a.unique_trait_count, e.unique_trait_count);
      assert.ok(
        Math.abs(a.score - e.score) <= 1e-12,
        `${a.score} vs ${e.score}`,
      );
    }
  });
test("malformed inputs fail explicitly", () => {
  for (const tokens of [
    [{ token_id: "x", traits: [] }],
    [{ token_id: "1", token_id_kind: "bad", traits: [] }],
    [{ token_id: "1", traits: [{ trait_type: "a", value: true }] }],
  ])
    assert.throws(() => scoreCollection({ tokens }));
  assert.throws(
    () =>
      scoreCollection({
        tokens: [
          {
            token_id: "1",
            traits: [{ trait_type: "a", value: 9007199254740993 }],
          },
        ],
      }),
    /exact large/,
  );
});

test("exact JSON decimals remain distinct", () => {
  const source =
    '{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":0.100000000000000001}]},{"token_id":"2","traits":[{"trait_type":"Level","value":0.100000000000000002}]}]}';
  const r = scoreCollection(parseCollectionJson(source), {
    trait_count: "exclude",
    traits: [{ trait_type: "Level", mode: "higher_is_rarer" }],
  });
  assert.deepEqual(
    r.map((t) => t.token_id),
    ["2", "1"],
  );
  assert.deepEqual(
    r.map((t) => t.score),
    [1, 0],
  );
});
