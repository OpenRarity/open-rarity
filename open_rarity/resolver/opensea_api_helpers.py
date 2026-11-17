"""OpenSea v2 fetching, separate from the pure scoring library."""

import logging
import os
import time
from collections.abc import Iterator
from urllib.parse import quote

import requests

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import (
    DateAttribute,
    NumericAttribute,
    StringAttribute,
    TokenMetadata,
)
from open_rarity.models.token_standard import TokenStandard
from open_rarity.resolver.models.collection_with_metadata import CollectionWithMetadata

logger = logging.getLogger("open_rarity_logger")
OS_METADATA_TRAIT_TYPE = "display_type"


class ERCStandardError(ValueError):
    pass


class OpenSeaClient:
    """Bounded, read-only v2 client. Keys are read when the client is created."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        testnet: bool = False,
        session: requests.Session | None = None,
        timeout: float = 30,
    ):
        self._key = (
            api_key
            if api_key is not None
            else os.environ.get("OPENSEA_API_KEY", os.environ.get("OS_API_KEY", ""))
        )
        self._session = session or requests.Session()
        self._owns_session = session is None
        self.timeout = timeout
        self.base_url = (
            "https://testnets-api.opensea.io/api/v2"
            if testnet
            else "https://api.opensea.io/api/v2"
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._owns_session:
            self._session.close()

    def _get(self, path: str, params: dict | None = None) -> dict:
        for attempt in range(3):
            response = self._session.get(
                self.base_url + path,
                params=params,
                headers={"Accept": "application/json", "X-API-KEY": self._key},
                timeout=self.timeout,
                allow_redirects=False,
            )
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                try:
                    delay = min(
                        30.0,
                        max(
                            0.0, float(response.headers.get("Retry-After", 2**attempt))
                        ),
                    )
                except ValueError:
                    delay = float(2**attempt)
                response.close()
                time.sleep(delay)
                continue
            try:
                response.raise_for_status()
                if response.status_code != 200:
                    raise ValueError("Unexpected OpenSea response status")
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("Expected an OpenSea response object")
                return data
            finally:
                response.close()
        raise RuntimeError("OpenSea retry limit reached")

    def collection(self, slug: str) -> dict:
        return self._get("/collections/" + quote(slug, safe=""))

    def nft(self, chain: str, contract: str, token_id: str) -> dict:
        path = "/chain/{}/contract/{}/nfts/{}".format(
            *(quote(v, safe="") for v in (chain, contract, token_id))
        )
        return self._get(path)["nft"]

    def iter_nfts(
        self, slug: str, *, page_size: int = 200, max_pages: int = 10000
    ) -> Iterator[dict]:
        if not 1 <= page_size <= 200 or max_pages < 1:
            raise ValueError("page_size must be 1..200 and max_pages must be positive")
        cursor = None
        cursors: set[str] = set()
        seen: set[tuple[str, str]] = set()
        for _ in range(max_pages):
            params: dict = {"limit": page_size}
            if cursor is not None:
                params["next"] = cursor
            page = self._get("/collection/" + quote(slug, safe="") + "/nfts", params)
            if not isinstance(page.get("nfts"), list):
                raise ValueError("OpenSea page is missing its nfts array")
            for nft in page["nfts"]:
                identity = (nft["contract"].lower(), nft["identifier"])
                if identity in seen:
                    raise ValueError(
                        "Duplicate NFT across OpenSea pages; retry the snapshot"
                    )
                seen.add(identity)
                yield nft
            cursor = page.get("next")
            if not cursor:
                return
            if not isinstance(cursor, str) or cursor in cursors:
                raise ValueError("OpenSea pagination cursor repeated or is invalid")
            cursors.add(cursor)
        raise ValueError("OpenSea pagination exceeded max_pages; no complete snapshot")


def _contract_chain(collection: dict, chain: str | None) -> tuple[str, set[str]]:
    contracts = collection["contracts"]
    chains = {c["chain"] for c in contracts}
    if chain is None:
        if len(chains) != 1:
            raise ValueError("Specify chain for a multi-chain collection")
        chain = next(iter(chains))
    addresses = {c["address"].lower() for c in contracts if c["chain"] == chain}
    if not addresses:
        raise ValueError("Collection has no contracts on the requested chain")
    # Collection pagination lacks a chain field, so identical addresses on two chains
    # cannot be distinguished safely.
    if any(
        c["chain"] != chain and c["address"].lower() in addresses for c in contracts
    ):
        raise ValueError("Collection has ambiguous contract addresses across chains")
    return chain, addresses


def _token(nft: dict) -> Token:
    if nft["token_standard"].lower() != "erc721":
        raise ERCStandardError("Only ERC721 collection scoring is supported")
    return Token(
        EVMContractTokenIdentifier(nft["contract"], int(nft["identifier"])),
        TokenStandard.ERC721,
        opensea_traits_to_token_metadata(nft["traits"]),
    )


def fetch_opensea_collection_data(slug: str, *, testnet: bool = False) -> dict:
    """Return the v2 collection response (no v1 wrapper)."""
    with OpenSeaClient(testnet=testnet) as client:
        return client.collection(slug)


def get_collection_from_opensea(
    slug: str,
    batch_size: int = 200,
    use_cache: bool = False,
    *,
    chain: str | None = None,
    testnet: bool = False,
) -> Collection:
    """Fetch every cursor page, including sparse IDs. Legacy disk caches are retired."""
    return get_collection_with_metadata_from_opensea(
        slug, use_cache, chain=chain, testnet=testnet, batch_size=batch_size
    ).collection


def get_collection_with_metadata_from_opensea(
    opensea_collection_slug: str,
    use_cache: bool = False,
    *,
    chain: str | None = None,
    testnet: bool = False,
    batch_size: int = 200,
) -> CollectionWithMetadata:
    # Never reuse the v1 cache: it can omit sparse IDs and empty metadata tokens.
    with OpenSeaClient(testnet=testnet) as client:
        data = client.collection(opensea_collection_slug)
        _, addresses = _contract_chain(data, chain)
        tokens = [
            _token(nft)
            for nft in client.iter_nfts(opensea_collection_slug, page_size=batch_size)
            if nft["contract"].lower() in addresses
        ]
    collection = Collection(name=data["name"], tokens=tokens)
    return CollectionWithMetadata(
        collection, sorted(addresses), len(tokens), opensea_collection_slug
    )


def get_tokens_from_opensea(
    opensea_slug: str,
    token_ids: list[int],
    *,
    chain: str | None = None,
    contract: str | None = None,
    testnet: bool = False,
) -> list[Token]:
    """Fetch explicit identifiers without assuming a contiguous supply."""
    with OpenSeaClient(testnet=testnet) as client:
        chain, addresses = _contract_chain(client.collection(opensea_slug), chain)
        if contract is None:
            if len(addresses) != 1:
                raise ValueError("Specify contract for a multi-contract collection")
            contract = next(iter(addresses))
        if contract.lower() not in addresses:
            raise ValueError("Contract is not in this collection on this chain")
        nfts = [client.nft(chain, contract, str(i)) for i in token_ids]
        if any(nft["collection"] != opensea_slug for nft in nfts):
            raise ValueError("NFT does not belong to the requested collection")
        return [_token(nft) for nft in nfts]


def opensea_traits_to_token_metadata(asset_traits: list) -> TokenMetadata:
    """Converts asset traits list returned by opensea assets API and converts
    it into a TokenMetadata.

    Parameters
    ----------
    asset_traits : list
        the "traits" field for an asset in the return value of Opensea's asset(s)
        endpoint.

    Returns
    -------
    TokenMetadata
        A TokenMetadata instance to hold the token metadata extracted from the
        input data.
    """

    string_attr = {}
    numeric_attr = {}
    date_attr = {}

    for trait in asset_traits:
        if is_string_trait(trait):
            string_attr[trait["trait_type"]] = StringAttribute(
                name=trait["trait_type"],
                value=trait["value"],
            )
        elif is_numeric_trait(trait):
            numeric_attr[trait["trait_type"]] = NumericAttribute(
                name=trait["trait_type"],
                value=trait["value"],
            )
        elif is_date_trait(trait):
            date_attr[trait["trait_type"]] = DateAttribute(
                name=trait["trait_type"],
                value=trait["value"],
            )
        else:
            logger.debug(f"Unknown trait type {trait}")

    return TokenMetadata(
        string_attributes=string_attr,
        numeric_attributes=numeric_attr,
        date_attributes=date_attr,
    )


# NFT metadata standard type definitions described here:
# https://docs.opensea.io/docs/metadata-standards
def is_string_trait(trait: dict) -> bool:
    """Helper method to verify string trait"""
    return trait.get(OS_METADATA_TRAIT_TYPE) is None and isinstance(
        trait.get("value"), str
    )


def is_numeric_trait(trait: dict) -> bool:
    """Helper method to verify numeric trait"""
    display_type = trait.get(OS_METADATA_TRAIT_TYPE)
    if display_type is None:
        value = trait.get("value")
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return display_type in [
        "number",
        "boost_percentage",
        "boost_number",
    ]


def is_date_trait(trait: dict) -> bool:
    """Helper method to verify date trait"""
    return trait.get(OS_METADATA_TRAIT_TYPE) == "date"
