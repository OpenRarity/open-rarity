import assert from "node:assert/strict";
import test from "node:test";
import { parseCreatorRarityConfig } from "../dist/index.js";

test("parses direct and contractURI rarity settings", () => {
  const rarity = {
    trait_count: "exclude",
    traits: [
      { trait_type: " Level ", mode: "exclude" },
      { trait_type: "Level", mode: "higher_is_rarer" },
      { trait_type: "level", mode: "exclude" },
    ],
  };
  const expected = {
    trait_count: "exclude",
    traits: [
      { trait_type: "Level", mode: "higher_is_rarer" },
      { trait_type: "level", mode: "exclude" },
    ],
  };
  assert.deepEqual(parseCreatorRarityConfig(rarity), expected);
  assert.deepEqual(parseCreatorRarityConfig({ rarity }), expected);
});

test("skips malformed entries without hiding valid ones", () => {
  const config = parseCreatorRarityConfig({
    trait_count: "unknown",
    traits: [
      null,
      { trait_type: 123, mode: "exclude" },
      { trait_type: " ", mode: "exclude" },
      { trait_type: "x".repeat(257), mode: "exclude" },
      { trait_type: "meta_trait:trait_count", mode: "exclude" },
      { trait_type: "Hat", mode: "invalid" },
      { trait_type: "Hat", mode: "exclude" },
      { trait_type: "Hat", mode: null },
    ],
  });
  assert.deepEqual(config, { traits: [{ trait_type: "Hat", mode: "exclude" }] });
  assert.deepEqual(parseCreatorRarityConfig({ rarity: [] }), {});
});

test("reads only the first 100 entries", () => {
  const traits = Array.from({ length: 100 }, (_, index) => ({
    trait_type: `Trait ${index}`,
    mode: "exclude",
  }));
  traits.push({ trait_type: "Too late", mode: "exclude" });
  const result = parseCreatorRarityConfig({ traits });
  assert.equal(result.traits.length, 100);
  assert.equal(result.traits.some((entry) => entry.trait_type === "Too late"), false);
});
