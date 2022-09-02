import logging
import math

import requests
from requests.models import HTTPError

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
            f"Received {response.status_code}: {response.reason}. {response.json()}"
        )

        response.raise_for_status()

    return response.json()["collection"]


def fetch_opensea_assets_data(
    slug: str, token_ids: list[int], limit=30
) -> list[dict]:
    """Fetches asset data from Opensea's GET assets endpoint for the given token ids

    Parameters
    ----------
    slug: str
        Opensea collection slug
    token_ids: list[int]
        the token id
    limit: int, optional
        How many to fetch at once. Defaults to 30, with a max of 30, by default 30.

    Returns
    -------
    list[dict]
        list of asset data dictionaries, e.g. the response in "assets" field,
        sorted by token_id asc

    Raises
    ------
        Exception: If api request fails


    """
    assert len(token_ids) <= limit
    # Max 30 limit enforced on API
    assert limit <= 30
    querystring = {
        "token_ids": token_ids,
        "collection_slug": slug,
        "offset": "0",
        "limit": limit,
    }

    response = requests.request(
        "GET",
        OS_ASSETS_URL,
        headers=HEADERS,
        params=querystring,
    )

    if response.status_code != 200:
        logger.debug(
            f"[Opensea] Failed to resolve assets for {slug}."
            f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    # The API does not sort return value assets by token ID, so sort then return
    return sorted(
        response.json()["assets"], key=(lambda a: int(a["token_id"]))
    )


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


def get_tokens_from_opensea(
    opensea_slug: str, token_ids: list[int]
) -> list[Token]:
    """Fetches eth nft data from opensea API and stores them into Token objects

    Parameters
    ----------
    opensea_slug : str
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
    try:
        assets = fetch_opensea_assets_data(
            slug=opensea_slug, token_ids=token_ids
        )
    except HTTPError as e:
        logger.exception(
            "FAILED: get_assets: could not fetch opensea assets for %s: %s",
            token_ids,
            e,
            exc_info=True,
        )
        raise

    tokens = []
    for asset in assets:
        token_metadata = opensea_traits_to_token_metadata(
            asset_traits=asset["traits"]
        )
        asset_contract_address = asset["asset_contract"]["address"]
        asset_contract_type = asset["asset_contract"]["asset_contract_type"]
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
        slug=opensea_collection_slug
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
        opensea_slug=opensea_collection_slug,
    )

    return collection_with_metadata


def get_collection_from_opensea(
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
    num_batches = math.ceil(total_supply / batch_size)
    initial_token_id = 0

    # Returns a list of `batch_size` token IDs, such that no token ID
    # can exceed `max_token_id` (in which case len(return_value) < `batch_size`)
    def get_token_ids(
        batch_id: int, max_token_id: int = total_supply - 1
    ) -> list[int]:
        token_id_start = initial_token_id + (batch_id * batch_size)
        token_id_end = int(min(token_id_start + batch_size - 1, max_token_id))
        return list(range(token_id_start, token_id_end + 1))

    for batch_id in range(num_batches):
        token_ids = get_token_ids(batch_id)
        tokens_batch = get_tokens_from_opensea(
            opensea_slug=opensea_collection_slug, token_ids=token_ids
        )

        tokens.extend(tokens_batch)

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
