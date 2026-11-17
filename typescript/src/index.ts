/** Inputs and results shared by the Python and TypeScript conformance fixtures. */
export type TraitValue = string | number | null;

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

const TRAIT_COUNT = "meta_trait:trait_count";

interface PreparedToken {
  input: TokenInput;
  index: number;
  values: Map<string, string>;
}

/** Score a complete categorical collection using the 0.7.5 compatibility rules. */
export function scoreCollection(collection: CollectionInput): TokenRarityResult[] {
  const tokens = collection.tokens.map((input, index): PreparedToken => {
    const values = new Map<string, string>();
    for (const trait of input.traits) {
      if (typeof trait.value !== "string") {
        throw new TypeError("Numeric and null traits require creator config support");
      }
      const name = trait.trait_type.trim().toLowerCase();
      const value = trait.value.trim().toLowerCase();
      values.set(name, value);
    }
    let traitCount = 0;
    for (const [name, value] of values) {
      if (name !== TRAIT_COUNT && value !== "" && value !== "none") traitCount++;
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
    for (const [name, counts] of frequencies) {
      const value = token.values.get(name);
      const count = value === undefined ? missingCounts.get(name) : counts.get(value);
      if (count === undefined || count <= 0) {
        throw new Error(`Invalid frequency for trait ${name}`);
      }
      points += Math.log2(total / count);
      if (value !== undefined && count === 1) unique++;
    }
    return {
      token_id: token.input.token_id,
      score: points / entropy,
      rank: 0,
      unique_trait_count: unique,
      kind: token.input.token_id_kind ?? "evm",
      index: token.index,
    };
  });

  results.sort((a, b) =>
    b.unique_trait_count - a.unique_trait_count ||
    b.score - a.score ||
    compareTokenIds(a, b) ||
    a.index - b.index,
  );
  for (let index = 0; index < results.length; index++) {
    const previous = results[index - 1];
    results[index].rank = previous !== undefined && nearlyEqual(results[index].score, previous.score)
      ? previous.rank
      : index + 1;
  }
  return results.map(({ token_id, score, rank, unique_trait_count }) => ({
    token_id, score, rank, unique_trait_count,
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
  return a.token_id < b.token_id ? -1 : a.token_id > b.token_id ? 1 : 0;
}
