import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { scoreCollection } from "../dist/index.js";

const fixtures = JSON.parse(
  readFileSync(new URL("../../tests/fixtures/legacy_075.json", import.meta.url), "utf8"),
);

for (const fixture of fixtures.cases) {
  test(`0.7.5 compatibility: ${fixture.name}`, () => {
    const collection = {
      tokens: fixture.tokens.map((token) => ({
        token_id: String(token.id),
        traits: Object.entries(token.attributes).map(([trait_type, value]) => ({
          trait_type, value,
        })),
      })),
    };
    const actual = scoreCollection(collection);
    assert.equal(actual.length, fixture.expected.length);
    for (const [index, expected] of fixture.expected.entries()) {
      assert.equal(actual[index].token_id, String(expected.id));
      assert.equal(actual[index].rank, expected.rank);
      assert.equal(actual[index].unique_trait_count, expected.unique_traits);
      assert.ok(Math.abs(actual[index].score - expected.score) <= 1e-12);
    }
  });
}

test("empty and single-token collections", () => {
  assert.deepEqual(scoreCollection({ tokens: [] }), []);
  assert.deepEqual(
    scoreCollection({ tokens: [{ token_id: "0", traits: [] }] }),
    [{ token_id: "0", score: 0, rank: 1, unique_trait_count: 1 }],
  );
});

test("numeric EVM IDs and raw mint IDs sort independently", () => {
  const tokens = [
    { token_id: "10", traits: [] },
    { token_id: "2", traits: [] },
    { token_id: "1", token_id_kind: "raw", traits: [] },
  ];
  assert.deepEqual(
    scoreCollection({ tokens }).map((item) => item.token_id),
    ["2", "10", "1"],
  );
});

test("duplicate IDs and unsupported values fail clearly", () => {
  assert.throws(
    () => scoreCollection({ tokens: [
      { token_id: "1", traits: [] },
      { token_id: "1", traits: [] },
    ] }),
    /Duplicate token ID/,
  );
  assert.throws(
    () => scoreCollection({ tokens: [
      { token_id: "1", traits: [{ trait_type: "Level", value: 5 }] },
    ] }),
    /Numeric and null traits require creator config support/,
  );
});
