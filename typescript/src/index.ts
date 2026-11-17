import { trim } from "./text.js";
import { ExactDecimal, decimalText } from "./decimal.js";
import {
  scoreConfigured,
  validateCollection,
  compareText,
} from "./configured.js";
import { parseCreatorRarityConfig } from "./config.js";
/** Inputs and results shared by the Python and TypeScript conformance fixtures. */
export type TraitValue = string | number | ExactDecimal | null;

export interface TraitInput {
  trait_type: string;
  value: TraitValue;
  display_type?: string | null;
}

export interface TokenInput {
  token_id: string;
  /** Use raw for mint addresses, including addresses made entirely of digits. */
  token_id_kind?: "evm" | "raw";
  traits: readonly TraitInput[];
}

export interface CollectionInput {
  tokens: readonly TokenInput[];
}

export type RarityMode = "exclude" | "higher_is_rarer";

export interface CreatorTraitSetting {
  trait_type: string;
  mode: RarityMode;
}

export interface CreatorRarityConfig {
  trait_count?: RarityMode;
  traits?: readonly CreatorTraitSetting[];
}

export interface TokenRarityResult {
  token_id: string;
  score: number;
  rank: number;
  unique_trait_count: number;
}

export interface SourceTrait {
  trait_type: string;
  value: string | null;
  value_kind: "string" | "number" | "null";
  display_type: string | null;
}
export interface TraitExplanation {
  trait_type: string;
  value: string | null;
  mode: "frequency" | "higher_is_rarer" | "exclude";
  count: number | null;
  probability: number | null;
  information: number;
  contribution: number;
  unique: boolean;
}
export interface ExplainedToken {
  result: TokenRarityResult;
  normalization: number;
  traits: TraitExplanation[];
  source_traits: SourceTrait[];
}
export type ExplanationDetails = Map<
  string,
  Pick<ExplainedToken, "normalization" | "traits">
>;

/** Score once, retaining source entries and explaining each selected trait. */
export function explainCollection(
  collection: CollectionInput,
  config?: CreatorRarityConfig,
): ExplainedToken[] {
  const details: ExplanationDetails = new Map();
  const results = scoreCollectionInternal(collection, config, details);
  const sources = new Map(collection.tokens.map(t => [t.token_id, t]));
  return results.map(result => ({
    result,
    ...details.get(result.token_id)!,
    source_traits: sources.get(result.token_id)!.traits.map(t => ({
      trait_type: t.trait_type,
      value: t.value === null
        ? null
        : typeof t.value === "string"
          ? t.value
          : decimalText(t.value instanceof ExactDecimal ? t.value.source : String(t.value)),
      value_kind: t.value === null ? "null" : typeof t.value === "string" ? "string" : "number",
      display_type: t.display_type ?? null,
    })),
  }));
}

export { parseCreatorRarityConfig } from "./config.js";

const TRAIT_COUNT = "meta_trait:trait_count";

interface PreparedToken {
  input: TokenInput;
  index: number;
  values: Map<string, string>;
}

/** Score a complete categorical collection using the 0.7.5 compatibility rules. */
export function scoreCollection(
  collection: CollectionInput,
  config?: CreatorRarityConfig,
): TokenRarityResult[] {
  return scoreCollectionInternal(collection, config);
}

function scoreCollectionInternal(
  collection: CollectionInput,
  config?: CreatorRarityConfig,
  details?: ExplanationDetails,
): TokenRarityResult[] {
  validateCollection(collection);
  const parsed = parseCreatorRarityConfig(config);
  if (
    parsed.trait_count ||
    parsed.traits?.length ||
    collection.tokens.some((t) =>
      t.traits.some((a) => typeof a.value !== "string"),
    )
  ) {
    return scoreConfigured(collection, parsed, details);
  }
  const tokens = collection.tokens.map((input, index): PreparedToken => {
    const values = new Map<string, string>();
    for (const trait of input.traits) {
      if (typeof trait.value !== "string") {
        throw new TypeError(
          "Numeric and null traits require creator config support",
        );
      }
      const name = trim(trait.trait_type).toLowerCase();
      const value = trim(trait.value).toLowerCase();
      values.set(name, value);
    }
    let traitCount = 0;
    for (const [name, value] of values) {
      if (name !== TRAIT_COUNT && value !== "" && value !== "none")
        traitCount++;
    }
    values.set(TRAIT_COUNT, String(traitCount));
    return { input, index, values };
  });

  const ids = new Set<string>();
  for (const token of tokens) {
    if (ids.has(token.input.token_id)) {
      throw new TypeError(`Duplicate token ID: ${token.input.token_id}`);
    }
    ids.add(token.input.token_id);
  }
  if (tokens.length === 0) return [];

  const frequencies = new Map<string, Map<string, number>>();
  for (const token of tokens) {
    for (const [name, value] of token.values) {
      let counts = frequencies.get(name);
      if (counts === undefined) {
        counts = new Map<string, number>();
        frequencies.set(name, counts);
      }
      counts.set(value, (counts.get(value) ?? 0) + 1);
    }
  }

  const total = tokens.length;
  let entropy = 0;
  const missingCounts = new Map<string, number>();
  for (const [name, counts] of frequencies) {
    let present = 0;
    for (const count of counts.values()) {
      present += count;
      const p = count / total;
      entropy -= p * Math.log2(p);
    }
    if (present < total) {
      const missing = total - present;
      missingCounts.set(name, missing);
      const p = missing / total;
      entropy -= p * Math.log2(p);
    }
  }
  if (entropy === 0) entropy = 1;

  const results = tokens.map((token) => {
    let points = 0;
    let unique = 0;
    const traits: TraitExplanation[] = [];
    for (const [name, counts] of frequencies) {
      const value = token.values.get(name);
      const count =
        value === undefined ? missingCounts.get(name) : counts.get(value);
      if (count === undefined || count <= 0) {
        throw new Error(`Invalid frequency for trait ${name}`);
      }
      const information = Math.log2(total / count);
      points += information;
      if (details) traits.push({
        trait_type: name, value: value ?? null, mode: "frequency", count,
        probability: count / total, information,
        contribution: information / entropy,
        unique: value !== undefined && count === 1,
      });
      if (value !== undefined && count === 1) unique++;
    }
    if (details) details.set(token.input.token_id, {
      normalization: entropy,
      traits: traits.sort((a, b) => compareText(a.trait_type, b.trait_type)),
    });
    return {
      token_id: token.input.token_id,
      score: points / entropy,
      rank: 0,
      unique_trait_count: unique,
      kind: token.input.token_id_kind ?? "evm",
      index: token.index,
    };
  });

  results.sort(
    (a, b) =>
      b.unique_trait_count - a.unique_trait_count ||
      b.score - a.score ||
      compareTokenIds(a, b) ||
      a.index - b.index,
  );
  for (let index = 0; index < results.length; index++) {
    const previous = results[index - 1];
    results[index].rank =
      previous !== undefined &&
      nearlyEqual(results[index].score, previous.score)
        ? previous.rank
        : index + 1;
  }
  return results.map(({ token_id, score, rank, unique_trait_count }) => ({
    token_id,
    score,
    rank,
    unique_trait_count,
  }));
}

function nearlyEqual(a: number, b: number): boolean {
  return Math.abs(a - b) <= 1e-9 * Math.max(Math.abs(a), Math.abs(b));
}

function compareTokenIds(
  a: { token_id: string; kind: "evm" | "raw" },
  b: { token_id: string; kind: "evm" | "raw" },
): number {
  const aNumeric = a.kind === "evm" && /^[0-9]+$/.test(a.token_id);
  const bNumeric = b.kind === "evm" && /^[0-9]+$/.test(b.token_id);
  if (aNumeric !== bNumeric) return aNumeric ? -1 : 1;
  if (aNumeric && bNumeric) {
    const left = BigInt(a.token_id);
    const right = BigInt(b.token_id);
    if (left !== right) return left < right ? -1 : 1;
  }
  return compareText(a.token_id, b.token_id);
}

/** Parse numeric trait values from their original JSON spelling, without rounding. */
export function parseCollectionJson(text: string): CollectionInput {
  const result = JSON.parse(text, ((
    key: string,
    value: unknown,
    context?: { source?: string },
  ) => {
    if (typeof value !== "number") return value;
    if (!context?.source)
      throw new TypeError(
        "Exact JSON parsing requires a runtime with JSON reviver source support",
      );
    return new ExactDecimal(context.source);
  }) as Parameters<typeof JSON.parse>[1]);
  validateCollection(result);
  return result;
}
export { ExactDecimal } from "./decimal.js";
