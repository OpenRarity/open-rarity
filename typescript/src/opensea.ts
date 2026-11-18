import { ExactDecimal } from "./decimal.js";
import type { CollectionInput, TokenInput, TraitInput } from "./index.js";

export interface OpenSeaCollectionOptions {
  apiKey: string;
  chain?: string;
  contract?: string;
  testnet?: boolean;
  pageSize?: number;
  maxPages?: number;
  signal?: AbortSignal;
  fetch?: typeof globalThis.fetch;
}

function object(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    throw new TypeError("Expected an OpenSea response object");
  return value as Record<string, unknown>;
}

function field(value: unknown, name: string): string {
  if (typeof value !== "string" || !value)
    throw new TypeError(`Invalid OpenSea ${name}`);
  return value;
}

function trait(value: unknown): TraitInput {
  const row = object(value);
  const { value: source, display_type } = row;
  if (!(source === null || typeof source === "string" || source instanceof ExactDecimal))
    throw new TypeError("Invalid OpenSea trait value");
  if (display_type != null && typeof display_type !== "string")
    throw new TypeError("Invalid OpenSea display_type");
  if (typeof row.trait_type !== "string")
    throw new TypeError("Invalid OpenSea trait_type");
  return { trait_type: row.trait_type, value: source, display_type };
}

/** Fetch all pages and return ordered input for a single ERC721 contract. */
export async function fetchOpenSeaCollection(
  slug: string,
  options: OpenSeaCollectionOptions,
): Promise<CollectionInput> {
  if (!/^[a-z0-9_-]+$/i.test(slug)) throw new TypeError("Invalid OpenSea slug");
  if (typeof options.apiKey !== "string" || !options.apiKey.trim()) throw new TypeError("An OpenSea API key is required");
  const { pageSize = 200, maxPages = 10000, fetch: request = globalThis.fetch } = options;
  if (!Number.isInteger(pageSize) || pageSize < 1 || pageSize > 200 ||
      !Number.isSafeInteger(maxPages) || maxPages < 1)
    throw new RangeError("pageSize must be 1..200 and maxPages must be a positive integer");
  const base = options.testnet
    ? "https://testnets-api.opensea.io/api/v2"
    : "https://api.opensea.io/api/v2";

  async function get(path: string, exactTraits = false) {
    const timeout = AbortSignal.timeout(30_000);
    const signal = options.signal ? AbortSignal.any([timeout, options.signal]) : timeout;
    const response = await request(base + path, {
      headers: { Accept: "application/json", "X-API-KEY": options.apiKey },
      redirect: "error",
      signal,
    });
    if (response.status !== 200) {
      await response.body?.cancel();
      throw new Error(`OpenSea returned HTTP ${response.status}`);
    }
    const body = await response.text();
    return object(JSON.parse(body, function (this: Record<string, unknown>, key, value, context?: { source?: string }) {
      if (exactTraits && key === "value" && typeof this.trait_type === "string" && typeof value === "number") {
        if (context?.source === undefined)
          throw new TypeError("Exact trait parsing requires JSON reviver source support");
        return new ExactDecimal(context.source);
      }
      return value;
    }));
  }

  const metadata = await get(`/collections/${slug}`);
  if (!Array.isArray(metadata.contracts))
    throw new TypeError("Expected OpenSea collection contracts");
  const contracts = metadata.contracts.map(value => {
    const row = object(value);
    return { chain: field(row.chain, "chain"), address: field(row.address, "address").toLowerCase() };
  });
  const chains = new Set(contracts.map(row => row.chain));
  const chain = options.chain ?? (chains.size === 1 ? contracts[0].chain : undefined);
  if (!chain) throw new Error("Specify a chain for an OpenSea collection with multiple chains");
  const addresses = new Set(contracts.filter(row => row.chain === chain).map(row => row.address));
  const contract = options.contract?.toLowerCase() ?? (addresses.size === 1 ? [...addresses][0] : undefined);
  if (!contract || !addresses.has(contract))
    throw new Error("Specify a contract belonging to this collection on the selected chain");
  if (contracts.some(row => row.chain !== chain && row.address === contract))
    throw new Error("Collection pagination cannot distinguish this contract across chains");

  const tokens: TokenInput[] = [];
  const ids = new Set<string>();
  const cursors = new Set<string>();
  let cursor: string | undefined;
  for (let page = 0; page < maxPages; page++) {
    const params = new URLSearchParams({ limit: String(pageSize) });
    if (cursor !== undefined) params.set("next", cursor);
    const response = await get(`/collection/${slug}/nfts?${params}`, true);
    if (!Array.isArray(response.nfts)) throw new TypeError("Expected OpenSea NFT page");
    for (const value of response.nfts) {
      const nft = object(value);
      if (field(nft.contract, "contract").toLowerCase() !== contract) continue;
      if (field(nft.token_standard, "token standard").toLowerCase() !== "erc721")
        throw new Error("Only ERC721 collections are supported");
      const id = field(nft.identifier, "identifier");
      if (!/^(0|[1-9][0-9]*)$/.test(id) || ids.has(id))
        throw new Error("Invalid or duplicate OpenSea token identifier");
      if (!Array.isArray(nft.traits)) throw new TypeError("Expected OpenSea NFT traits");
      ids.add(id);
      tokens.push({ token_id: id, traits: nft.traits.map(trait) });
    }
    if (response.next == null || response.next === "") return { tokens };
    cursor = field(response.next, "pagination cursor");
    if (cursors.has(cursor)) throw new Error("OpenSea pagination cursor repeated");
    cursors.add(cursor);
  }
  throw new Error("OpenSea pagination exceeded maxPages");
}
