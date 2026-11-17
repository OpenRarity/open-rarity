import { trim } from "./text.js";
import type {
  CreatorRarityConfig,
  CreatorTraitSetting,
  RarityMode,
} from "./index.js";

const TRAIT_COUNT = "meta_trait:trait_count";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isMode(value: unknown): value is RarityMode {
  return value === "exclude" || value === "higher_is_rarer";
}

/** Parse a contractURI document or its rarity object without discarding valid entries. */
export function parseCreatorRarityConfig(input: unknown): CreatorRarityConfig {
  if (!isRecord(input)) return {};
  const rarity = "rarity" in input ? input.rarity : input;
  if (!isRecord(rarity)) return {};

  const byName = new Map<string, CreatorTraitSetting>();
  if (Array.isArray(rarity.traits)) {
    for (const entry of rarity.traits.slice(0, 100)) {
      if (
        !isRecord(entry) ||
        typeof entry.trait_type !== "string" ||
        !isMode(entry.mode)
      ) {
        continue;
      }
      const name = trim(entry.trait_type);
      if (name.length === 0 || name.length > 256 || name === TRAIT_COUNT)
        continue;
      byName.delete(name);
      byName.set(name, { trait_type: name, mode: entry.mode });
    }
  }

  const result: CreatorRarityConfig = {};
  if (isMode(rarity.trait_count)) result.trait_count = rarity.trait_count;
  if (byName.size > 0) result.traits = [...byName.values()];
  return result;
}
