import asyncio as aio
import logging
from itertools import chain

import httpx
import requests
from requests.models import HTTPError
from satchel import chunk
from tqdm.asyncio import tqdm_asyncio as tqdm_aio

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
from open_rarity.resolver.models.collection_with_metadata import (
    CollectionWithMetadata,
)

logger = logging.getLogger("open_rarity_logger")

# https://docs.opensea.io/reference/retrieving-a-single-collection
OS_COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
OS_ASSETS_URL = "https://api.opensea.io/api/v1/assets"

HEADERS = {
    "Accept": "application/json",
    "X-API-KEY": "",
}

# https://docs.opensea.io/docs/metadata-standards
OS_METADATA_TRAIT_TYPE = "display_type"


# Error is thrown if computatation is requested on a non-ERC721/1155
# token or collection. This is due to library only working for these
# standards currently.
class ERCStandardError(ValueError):
    pass


def fetch_opensea_collection_data(slug: str) -> dict:
    """Fetches collection data from Opensea's GET collection endpoint for
    the given slug.

    Raises:
        Exception: If API request fails
    """
    response = requests.get(OS_COLLECTION_URL.format(slug=slug))

    if response.status_code != 200:
        logger.debug(
            f"[Opensea] Failed to resolve collection {slug}."
            f"Received {response.status_code}: {response.text}. {response.json()}"
        )

        response.raise_for_status()

    return response.json()["collection"]


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


async def get_tokens_from_opensea(
    slug: str,
    token_ids: list[int],
    client: httpx.AsyncClient,
    sem: aio.BoundedSemaphore | aio.Semaphore,
) -> list[Token]:
    """Fetches eth nft data from opensea API and stores them into Token objects

    Parameters
    ----------
    slug : str
        Opensea collection slug
    token_ids : list[int]
        List of token ids to fetch for

    Returns
    -------
    list[Token]
        Returns list of tokens if request is successful.

    Raises
    ------
    ValueError
        if request is made to a non ERC721 or ERC1155 collection
    HTTPError
        if request to opensea fails
    """
    limit = 30
    try:
        async with sem:
            assert len(token_ids) <= limit
            # Max 30 limit enforced on API
            assert limit <= 30
            querystring = {
                "token_ids": token_ids,
                "collection_slug": slug,
                "offset": "0",
                "limit": limit,
            }
            if client:
                r = await client.get(
                    OS_ASSETS_URL,
                    headers=HEADERS,
                    params=querystring,
                )
            else:
                async with httpx.AsyncClient() as client:
                    r = await client.get(
                        OS_ASSETS_URL,
                        headers=HEADERS,
                        params=querystring,
                    )

            if r.status_code != 200:
                logger.debug(
                    f"[Opensea] Failed to resolve assets for {slug}."
                    f"Received {r.status_code}: {r.text}. {r.json()}"
                )
                r.raise_for_status()

            # The API does not sort return value assets by token ID, so sort then return
            tokens = []
            assets = sorted(
                r.json()["assets"], key=(lambda a: int(a["token_id"]))
            )
            for asset in assets:
                token_metadata = opensea_traits_to_token_metadata(
                    asset_traits=asset["traits"]
                )
                asset_contract_address = asset["asset_contract"]["address"]
                asset_contract_type = asset["asset_contract"][
                    "asset_contract_type"
                ]
                if asset_contract_type == "non-fungible":
                    token_standard = TokenStandard.ERC721
                elif asset_contract_type == "semi-fungible":
                    token_standard = TokenStandard.ERC1155
                else:
                    raise ValueError(
                        f"Unexpected asset contrat type: {asset_contract_type}"
                    )
                tokens.append(
                    Token(
                        token_identifier=EVMContractTokenIdentifier(
                            identifier_type="evm_contract",
                            contract_address=asset_contract_address,
                            token_id=int(asset["token_id"]),
                        ),
                        token_standard=token_standard,
                        metadata=token_metadata,
                    )
                )

    except HTTPError as e:
        logger.exception(
            "FAILED: get_assets: could not fetch opensea assets for %s: %s",
            token_ids,
            e,
            exc_info=True,
        )
        raise

    return tokens


def get_collection_with_metadata_from_opensea(
    opensea_collection_slug: str,
) -> CollectionWithMetadata:
    """Fetches collection metadata with OpenSea endpoint and API key
    and stores it in the Collection object with 0 tokens.

    Parameters
    ----------
    opensea_collection_slug : str
        collection slug on opensea's system

    Returns
    -------
    CollectionWithMetadata
        collection with metadata, but with no tokens

    """
    collection_obj = fetch_opensea_collection_data(
        opensea_slug=opensea_collection_slug
    )
    contracts = collection_obj["primary_asset_contracts"]
    interfaces = set([contract["schema_name"] for contract in contracts])
    stats = collection_obj["stats"]
    if not interfaces.issubset(set(["ERC721", "ERC1155"])):
        raise ERCStandardError(
            "We currently do not support non EVM standards at the moment"
        )

    collection = Collection(
        name=collection_obj["name"],
        attributes_frequency_counts=collection_obj["traits"],
        tokens=[],
    )

    collection_with_metadata = CollectionWithMetadata(
        collection=collection,
        contract_addresses=[contract["address"] for contract in contracts],
        token_total_supply=int(stats["total_supply"]),
        slug=opensea_collection_slug,
    )

    return collection_with_metadata


async def get_collection_from_opensea(
    opensea_collection_slug: str,
) -> Collection:
    """Fetches collection and token data with OpenSea endpoint and API key
    and stores it in the Collection object

    Parameters
    ----------
    opensea_collection_slug : str
        collection slug on opensea's system

    Returns
    -------
    Collection
        collection abstraction

    """
    # Fetch collection metadata
    collection_obj = fetch_opensea_collection_data(
        slug=opensea_collection_slug
    )
    contracts = collection_obj["primary_asset_contracts"]
    interfaces = set([contract["schema_name"] for contract in contracts])
    stats = collection_obj["stats"]
    if not interfaces.issubset(set(["ERC721", "ERC1155"])):
        raise ERCStandardError(
            "We currently do not support non EVM standards at the moment"
        )

    total_supply = int(stats["total_supply"])

    # Fetch token metadata
    tokens: list[Token] = []
    batch_size = 30
    initial_token_id = 0

    # Return list of lists for batched token_ids
    def batch_token_ids(
        intial_token_id: int = 0,
        max_token_id: int = total_supply - 1,
        batch_size: int = 30,
    ):
        token_ids = list(range(initial_token_id, max_token_id))
        return chunk(
            token_ids,
            batch_size,
            as_list=True,
        )

    # We need to bound the number of awaitables to avoid hitting the OS rate limit
    sem = aio.BoundedSemaphore(4)
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = [
            get_tokens_from_opensea(
                slug=opensea_collection_slug,
                token_ids=token_ids,
                client=client,
                sem=sem,
            )
            for token_ids in batch_token_ids(tokens, batch_size=batch_size)
        ]
        tokens = list(
            chain(
                *(
                    await tqdm_aio.gather(
                        *tasks,
                        desc=f"Fetch {opensea_collection_slug} Token Batches from OS",
                    )
                )
            )
        )

    collection = Collection(
        name=collection_obj["name"],
        attributes_frequency_counts=collection_obj["traits"],
        tokens=tokens,
    )

    return collection


# NFT metadata standard type definitions described here:
# https://docs.opensea.io/docs/metadata-standards
def is_string_trait(trait: dict) -> bool:
    """Helper method to verify string trait"""
    return trait[OS_METADATA_TRAIT_TYPE] is None


def is_numeric_trait(trait: dict) -> bool:
    """Helper method to verify numeric trait"""
    return trait[OS_METADATA_TRAIT_TYPE] in [
        "number",
        "boost_percentage",
        "boost_number",
    ]


def is_date_trait(trait: dict) -> bool:
    """Helper method to verify date trait"""
    return trait[OS_METADATA_TRAIT_TYPE] in ["date"]
