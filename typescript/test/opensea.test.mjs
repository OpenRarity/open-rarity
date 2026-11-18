import assert from "node:assert/strict";
import test from "node:test";
import { fetchOpenSeaCollection } from "../dist/opensea.js";
import { scoreCollection } from "../dist/index.js";

const metadata = { contracts: [{ chain: "ethereum", address: "0xAb" }] };
const page = (id, next) => ({
  nfts: [{ contract: "0xab", identifier: id, token_standard: "erc721", traits: [] }],
  next,
});

function mock(...bodies) {
  return async () => {
    assert.ok(bodies.length, "unexpected API request");
    return Response.json(bodies.shift());
  };
}

test("fetches sparse IDs in cursor order and retains ordered exact traits", async () => {
  let calls = 0;
  const tokens = await fetchOpenSeaCollection("example", {
    apiKey: "fixture",
    pageSize: 1,
    fetch: async (url, init) => {
      const { pathname, searchParams, hostname } = new URL(url);
      assert.equal(hostname, "api.opensea.io");
      assert.equal(init.headers["X-API-KEY"], "fixture");
      assert.equal(init.redirect, "error");
      assert.ok(init.signal instanceof AbortSignal);
      if (calls++ === 0) {
        assert.equal(pathname, "/api/v2/collections/example");
        return Response.json(metadata);
      }
      assert.equal(pathname, "/api/v2/collection/example/nfts");
      assert.equal(searchParams.get("limit"), "1");
      if (calls === 2) {
        assert.equal(searchParams.get("next"), null);
        return new Response('{"nfts":[{"contract":"0xab","identifier":"9007199254740993","token_standard":"erc721","traits":[{"trait_type":"Level","value":9007199254740993},{"trait_type":"Level","value":"10"}]}],"next":"a+&="}');
      }
      assert.equal(searchParams.get("next"), "a+&=");
      return Response.json(page("2", null));
    },
  });
  assert.equal(calls, 3);
  assert.deepEqual(tokens.tokens.map(token => token.token_id), ["9007199254740993", "2"]);
  assert.deepEqual(tokens.tokens[0].traits.map(row => row.value.source ?? row.value), ["9007199254740993", "10"]);
  assert.equal(scoreCollection(tokens).length, 2);
});

test("rejects ambiguous contract identity and incomplete pagination", async () => {
  const options = { apiKey: "fixture" };
  const multi = { contracts: [...metadata.contracts, { chain: "base", address: "0xab" }] };
  await assert.rejects(fetchOpenSeaCollection("example", { ...options, fetch: mock(multi) }), /Specify a chain/);
  await assert.rejects(fetchOpenSeaCollection("example", { ...options, chain: "ethereum", fetch: mock(multi) }), /across chains/);
  await assert.rejects(fetchOpenSeaCollection("example", { ...options, maxPages: 1, fetch: mock(metadata, page("1", "next")) }), /maxPages/);
  await assert.rejects(fetchOpenSeaCollection("example", { ...options, fetch: mock(metadata, page("1", "next"), page("2", "next")) }), /cursor repeated/);
  await assert.rejects(fetchOpenSeaCollection("example", { ...options, fetch: mock(metadata, page("1", "next"), page("1", null)) }), /duplicate/);
});

test("surfaces API errors without including the response body", async () => {
  await assert.rejects(fetchOpenSeaCollection("example", {
    apiKey: "fixture",
    fetch: async () => new Response("untrusted response body", { status: 429 }),
  }), { message: "OpenSea returned HTTP 429" });
});

test("selects one contract even when another contract shares its token IDs", async () => {
  const contracts = { contracts: [...metadata.contracts, { chain: "ethereum", address: "0xcd" }] };
  const response = page("1", null);
  response.nfts.unshift({ ...response.nfts[0], contract: "0xcd", token_standard: "erc1155" });
  const request = mock(contracts, response);
  const result = await fetchOpenSeaCollection("example", {
    apiKey: "fixture",
    contract: "0xAB",
    testnet: true,
    fetch: async (url, init) => {
      assert.equal(new URL(url).hostname, "testnets-api.opensea.io");
      return request(url, init);
    },
  });
  assert.deepEqual(result, { tokens: [{ token_id: "1", traits: [] }] });
});
