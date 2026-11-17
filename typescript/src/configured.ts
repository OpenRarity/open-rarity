import { log2 } from "./log2.js";
import { parseCreatorRarityConfig } from "./config.js";
import {
  decimal,
  decimalText,
  compareDecimals,
  ExactDecimal,
} from "./decimal.js";
import type {
  CollectionInput,
  CreatorRarityConfig,
  TokenRarityResult,
} from "./index.js";
const COUNT = "meta_trait:trait_count";
import { trim, compareText } from "./text.js";
export { compareText } from "./text.js";
export function validateCollection(collection: CollectionInput): void {
  if (!collection || !Array.isArray(collection.tokens))
    throw new TypeError("Expected a tokens array");
  const ids = new Set<string>();
  for (const token of collection.tokens) {
    if (!token || typeof token.token_id !== "string" || !token.token_id)
      throw new TypeError("Token IDs must be nonempty strings");
    const kind = token.token_id_kind ?? "evm";
    if (kind !== "evm" && kind !== "raw")
      throw new TypeError("Unknown token ID kind");
    if (kind === "evm" && !/^[0-9]+$/.test(token.token_id))
      throw new TypeError("EVM token IDs must contain unsigned decimal digits");
    if (ids.has(token.token_id)) throw new TypeError("Duplicate token ID");
    ids.add(token.token_id);
    if (!Array.isArray(token.traits))
      throw new TypeError("Expected a traits array");
    for (const trait of token.traits) {
      if (!trait || typeof trait.trait_type !== "string")
        throw new TypeError("Trait names must be strings");
      const v = trait.value;
      if (
        v !== null &&
        typeof v !== "string" &&
        typeof v !== "number" &&
        !(v instanceof ExactDecimal)
      )
        throw new TypeError("Invalid trait value");
      if (
        typeof v === "number" &&
        (!Number.isFinite(v) ||
          (Number.isInteger(v) && !Number.isSafeInteger(v)))
      )
        throw new TypeError(
          "Use parseCollectionJson for exact large numeric values",
        );
      if (trait.display_type != null && typeof trait.display_type !== "string")
        throw new TypeError("Invalid display_type");
    }
  }
}
export function scoreConfigured(
  collection: CollectionInput,
  input?: CreatorRarityConfig,
): TokenRarityResult[] {
  const config = parseCreatorRarityConfig(input);
  const configured = Boolean(config.trait_count || config.traits?.length);
  const modes = new Map(config.traits?.map((t) => [t.trait_type, t.mode]));
  if (config.trait_count) modes.set(COUNT, config.trait_count);
  const invalidDates: Set<string>[] = [];
  const selected = collection.tokens.map((token) => {
    const invalidDate = new Set<string>();
    invalidDates.push(invalidDate);
    const values = new Map<string, string>();
    for (const t of token.traits) {
      let name = trim(t.trait_type);
      if (name === COUNT || t.value === null) continue;
      let value = trim(
        t.value instanceof ExactDecimal
          ? decimalText(t.value.source)
          : typeof t.value === "number"
            ? decimalText(String(t.value))
            : t.value,
      );
      if (configured) {
        if (!value || value.toLowerCase() === "none") continue;
      } else {
        name = name.toLowerCase();
        value = value.toLowerCase();
      }
      if (
        !configured ||
        !values.has(name) ||
        compareText(value, values.get(name)!) < 0
      ) {
        values.set(name, value);
        invalidDate.delete(name);
        if (t.display_type === "date") {
          const d = decimal(value);
          if (!d || d.exponent < 0) invalidDate.add(name);
        }
      }
    }
    let count = 0;
    for (const [name, value] of values)
      if (!modes.has(name) && value !== "" && value.toLowerCase() !== "none")
        count++;
    if (config.trait_count !== "exclude") values.set(COUNT, String(count));
    for (const [name, mode] of modes)
      if (mode === "exclude") values.delete(name);
    return values;
  });
  const names = [...new Set(selected.flatMap((v) => [...v.keys()]))].sort(
      compareText,
    ),
    total = selected.length;
  const counts = new Map(
    names.map((name) => {
      const c = new Map<string | undefined, number>();
      for (const v of selected)
        c.set(v.get(name), (c.get(v.get(name)) ?? 0) + 1);
      return [name, c] as const;
    }),
  );
  let entropy = 0;
  for (const name of names)
    for (const count of counts.get(name)!.values()) {
      const p = count / total;
      entropy -= p * log2(p);
    }
  if (!entropy) entropy = 1;
  const numeric = new Map(
    names
      .filter((n) => modes.get(n) === "higher_is_rarer")
      .map((name) => [
        name,
        selected
          .map((v, i) =>
            invalidDates[i].has(name) ? null : decimal(v.get(name) ?? ""),
          )
          .filter((v) => v !== null)
          .sort(compareDecimals),
      ]),
  );
  const results = selected.map((v, index) => {
    let points = 0,
      unique = 0;
    for (const name of names) {
      const value = v.get(name),
        nums = numeric.get(name);
      if (nums) {
        const d = invalidDates[index].has(name) ? null : decimal(value ?? "");
        if (d) {
          let lo = 0,
            hi = nums.length;
          while (lo < hi) {
            const mid = (lo + hi) >>> 1;
            if (compareDecimals(nums[mid], d) < 0) lo = mid + 1;
            else hi = mid;
          }
          points -= log2((nums.length - lo) / total);
        }
      } else {
        const count = counts.get(name)!.get(value)!;
        points -= log2(count / total);
        if (value !== undefined && count === 1) unique++;
      }
    }
    return {
      token_id: collection.tokens[index].token_id,
      score: points / entropy,
      rank: 0,
      unique_trait_count: unique,
      index,
    };
  });
  results.sort((a, b) => {
    const d = b.unique_trait_count - a.unique_trait_count || b.score - a.score;
    if (d) return d;
    const an = (collection.tokens[a.index].token_id_kind ?? "evm") === "evm",
      bn = (collection.tokens[b.index].token_id_kind ?? "evm") === "evm";
    if (an !== bn) return an ? -1 : 1;
    if (an) {
      const x = BigInt(a.token_id),
        y = BigInt(b.token_id);
      if (x !== y) return x < y ? -1 : 1;
    }
    return compareText(a.token_id, b.token_id);
  });
  results.forEach((r, i) => {
    const prev = results[i - 1];
    r.rank =
      prev &&
      (configured
        ? r.score === prev.score
        : Math.abs(r.score - prev.score) <=
          1e-9 * Math.max(Math.abs(r.score), Math.abs(prev.score)))
        ? prev.rank
        : i + 1;
  });
  return results.map(({ index, ...result }) => result);
}
