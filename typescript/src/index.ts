/** Inputs and results shared by the Python and TypeScript conformance fixtures. */
export type TraitValue = string | number | null;

export interface TraitInput {
  trait_type: string;
  value: TraitValue;
  display_type?: string | null;
}

export interface TokenInput {
  token_id: string;
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
