import json
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

DEFAULT_OS_CACHE_FILENAME_PREFIX: str = "cached_data/cached_os_trait_data"


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


def get_all_collection_tokens(
    slug: str,
    total_supply: int,
    batch_size: int = 30,
    add_trait_count: bool = False,
    use_cache: bool = True,
    cache_file_prefix: str | None = DEFAULT_OS_CACHE_FILENAME_PREFIX,
) -> list[Token]:
    """Returns a list of Token's with all metadata filled, either populated
    from Opensea API or fetched from a local cache file.
    """
    cached_filename = f"{cache_file_prefix}-{slug}.json"
    tokens: list[Token] = []

    # For performance optimization and re-runs for the same collection,
    # we optionally check if an already cached file for the collection
    # data exists since they tend to be static.
    if use_cache:
        tokens = read_collection_data_from_file(
            filename=cached_filename,
            expected_supply=total_supply,
            slug=slug,
            add_trait_count=add_trait_count,
        )
    else:
        logger.info(
            f"Not using cache for fetching collection tokens for: {slug}"
        )

    # This means either cache file didn't exist or did not have data.
    # Fetch all token trait data from opensea.
    if len(tokens) == 0:
        tokens = []
        num_batches = math.ceil(total_supply / batch_size)
        initial_token_id = 0

        # Returns a list of `batch_size` token IDs, such that no token ID
        # can exceed `max_token_id` (in which case len(return_value) < `batch_size`)
        def get_token_ids(
            batch_id: int, max_token_id: int = total_supply - 1
        ) -> list[int]:
            token_id_start = initial_token_id + (batch_id * batch_size)
            token_id_end = int(
                min(token_id_start + batch_size - 1, max_token_id)
            )
            return list(range(token_id_start, token_id_end + 1))

        for batch_id in range(num_batches):
            token_ids = get_token_ids(batch_id)
            tokens_batch = get_tokens_from_opensea(
                opensea_slug=slug,
                token_ids=token_ids,
                add_trait_count=add_trait_count,
            )

            tokens.extend(tokens_batch)

        # It's possible for some collections to start at token id 1 instead of 0,
        # so attempt fetch of more tokens if they exist
        token_id = total_supply
        while True:
            try:
                extra_tokens = get_tokens_from_opensea(
                    opensea_slug=slug,
                    token_ids=[token_id],
                    add_trait_count=add_trait_count,
                )
                if len(extra_tokens) == 0:
                    break
                tokens.extend(extra_tokens)
                token_id += 1
            except Exception:
                break

        if len(tokens) > total_supply:
            logger.warning(
                f"Warning: Found more tokens ({len(tokens)}) than "
                f"token supply ({total_supply}) fetched from collection stats"
            )

        # Write to local disk the fetched data for later caching
        if use_cache:
            write_collection_data_to_file(
                filename=cached_filename, tokens=tokens
            )

    return tokens


def get_tokens_from_opensea(
    opensea_slug: str, token_ids: list[int], add_trait_count: bool = False
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
        if add_trait_count:
            # In opensea, we return none as explicit empty traits
            token_metadata.string_attributes[
                "trait_count"
            ] = get_trait_count_attribute(token_metadata)

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
    use_cache: bool,
    add_trait_count: bool = False,
) -> CollectionWithMetadata:
    """Fetches collection metadata with OpenSea endpoint and API key
    and stores it in the Collection object with 0 tokens.

    Parameters
    ----------
    opensea_collection_slug : str
        collection slug on opensea's system
    use_cache: bool
        If true, reads the token trait data from local cache file if it exists, or
        fetches from opensea api and stores the data in a local cached file for
        future reuse.

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
    total_supply = int(stats["total_supply"])
    tokens = get_all_collection_tokens(
        slug=opensea_collection_slug,
        total_supply=total_supply,
        use_cache=use_cache,
        add_trait_count=add_trait_count,
    )

    collection = Collection(name=collection_obj["name"], tokens=tokens)

    collection_with_metadata = CollectionWithMetadata(
        collection=collection,
        contract_addresses=[contract["address"] for contract in contracts],
        token_total_supply=max(total_supply, collection.token_total_supply),
        opensea_slug=opensea_collection_slug,
    )

    return collection_with_metadata


def get_collection_from_opensea(
    slug: str,
    batch_size: int = 30,
    add_trait_count: bool = False,
    use_cache: bool = True,
    cache_file_prefix: str | None = DEFAULT_OS_CACHE_FILENAME_PREFIX,
) -> Collection:
    """Fetches collection and token data with OpenSea endpoint and API key
    and stores it in the Collection object. If local cache file is used and
    contains all collection token data, that data will be used instead.

    Parameters
    ----------
    slug : str
        collection slug on opensea's system

    batch_size: int
        batch size for the opensea API requests
        maximum value is 30

    use_cache: bool
        set to True to look for a local cached version of the collection and token
        metadata fetched from opensea to prevent re-fetching.

    Returns
    -------
    Collection
        collection abstraction

    """
    # Fetch collection metadata
    collection_obj = fetch_opensea_collection_data(slug=slug)
    contracts = collection_obj["primary_asset_contracts"]
    interfaces = set([contract["schema_name"] for contract in contracts])
    stats = collection_obj["stats"]
    if not interfaces.issubset(set(["ERC721"])):
        raise ERCStandardError(
            "We currently do not support non ERC721 standards at the moment"
        )

    total_supply = int(stats["total_supply"])
    tokens = get_all_collection_tokens(
        slug=slug,
        total_supply=total_supply,
        batch_size=batch_size,
        add_trait_count=add_trait_count,
        use_cache=use_cache,
        cache_file_prefix=cache_file_prefix,
    )

    return Collection(name=collection_obj["name"], tokens=tokens)


def write_collection_data_to_file(filename: str, tokens: list[Token]):
    json_output = []
    for token in tokens:
        # Note: We assume EVM token here
        json_output.append(token.to_dict())
    with open(filename, "w+") as jsonfile:
        json.dump(json_output, jsonfile, indent=4)
    logger.info(f"Wrote token data to cache file: {filename}")


def read_collection_data_from_file(
    filename: str,
    expected_supply: int,
    slug: str,
    add_trait_count: bool = False,
) -> list[Token]:
    tokens = []
    try:
        with open(filename) as jsonfile:
            tokens_data = json.load(jsonfile)
            if len(tokens_data) != expected_supply:
                logger.warning(
                    "Warning: Data cache file for %s collection has data for %s tokens "
                    "but total supply fetched from opensea is %s",
                    slug,
                    len(tokens_data),
                    expected_supply,
                )
            if len(tokens_data) > 0:
                for token_data in tokens_data:
                    metadata_dict = token_data["metadata_dict"]
                    assert metadata_dict
                    # TODO vicky - hacky
                    if add_trait_count:
                        token_metadata = TokenMetadata.from_attributes(
                            metadata_dict
                        )
                        trait_count_attr = get_trait_count_attribute(
                            token_metadata
                        )
                        metadata_dict["trait_count"] = trait_count_attr.value
                    tokens.append(Token.from_dict(token_data))

        logger.debug(f"Read {len(tokens)} tokens from cache file: {filename}")
    except FileNotFoundError:
        logger.warning(f"No opensea cache file found for {slug}: {filename}")
    except Exception:
        logger.exception(
            "Failed to parse valid cache data for %s from %s",
            slug,
            filename,
            exc_info=True,
        )
        return []

    return tokens


def get_trait_count_attribute(
    token_metadata: TokenMetadata,
) -> StringAttribute:
    # In opensea, we return none as explicit empty traits
    trait_count = str(
        sum(
            map(
                lambda a: a.value.lower() != "none",
                token_metadata.string_attributes.values(),
            )
        )
    )
    return StringAttribute(name="trait_count", value=trait_count)


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
