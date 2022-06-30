import io
import json
import pkgutil
from time import process_time

import requests

from openrarity.models.collection import Collection
from openrarity.models.chain import Chain
from openrarity.models.token import Token
from openrarity.models.token_metadata import (
    StringAttributeValue,
    TokenMetadata,
)
from openrarity.resolver.rarity_providers.rarity_provider import (
    ExternalRarityProvider,
)
import logging
from time import strftime


OS_COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
OS_ASSETS_URL = "https://api.opensea.io/api/v1/assets"

HEADERS = {
    "Accept": "application/json",
    "X-API-KEY": "",
}


def get_collection_metadata(
    collection_slug: str, tokens: list[Token]
) -> Collection:
    """Resolves collection metadata with OpenSea endpoint and API key

    Parameters
    ----------
    collection_slug : str
        collection slug
    tokens : list[Token]
        list of tokens to resolve metadata

    Returns
    -------
    Collection
        collection abstraction

    Raises
    ------
    Exception
        _description_
    """
    collection_response = requests.get(
        OS_COLLECTION_URL.format(slug=collection_slug)
    )

    if collection_response.status_code != 200:
        logger.debug(
            "Failed to resolve collection {slug}. Reason {resp}".format(
                resp=collection_response, slug=collection_slug
            )
        )

        raise Exception(
            "Failed to resolve collection with slug {slug}".format(
                slug=collection_slug
            )
        )

    collection_obj = collection_response.json()["collection"]
    primary_contract = collection_obj["primary_asset_contracts"][0]
    stats = collection_obj["stats"]
    attribute_count = collection_obj["traits"]

    collection = Collection(
        name=primary_contract["name"],
        slug=collection_slug,
        contract_address=primary_contract["address"],
        creator_address="",
        token_standard=primary_contract["schema_name"],
        chain=Chain.ETH,
        token_total_supply=stats["total_supply"],
        tokens=tokens,
        attributes_count=attribute_count,
    )

    return collection


def get_assets(collection: Collection) -> list[Token]:
    """Resolves assets through OpenSea API asset endpoint.
        Augment metadata with Gem rankings from Gem, RaritySniper and TraitSniper.

    Parameters
    ----------
    collection : Collection
        collection

    Returns
    -------
    list[Token]
        provide list of tokens augmented with assets metadata and ranking provider
    """
    rarity_resolver = ExternalRarityProvider()
    batch_id = 0
    # TODO impreso@ handle the case with collections where mod 30 !=0
    range_end = int(collection.token_total_supply / 30)
    tokens: list[Token] = []

    t1_start = process_time()

    while batch_id < range_end:
        logger.debug(
            "Starting batch {num} for collection {collection}".format(
                num=batch_id, collection=collection.slug
            )
        )

        querystring = {
            "token_ids": [
                token_id
                for token_id in range(batch_id * 30 + 1, batch_id * 30 + 31)
            ],
            "collection_slug": collection.slug,
            "order_direction": "desc",
            "offset": "0",
        }

        response = requests.request(
            "GET", OS_ASSETS_URL, headers=HEADERS, params=querystring
        )

        if response.status_code != 200:
            logger.debug(
                "Failed to resolve token_ids. Reason {resp}".format(
                    resp=response
                )
            )
            break

        augment_tokens_batch: list[Token] = []
        assets = response.json()["assets"]

        # convert all tokens to local models
        for token in assets:
            # TODO filter out numeric traits
            token_metadata = TokenMetadata(
                string_attributes={
                    trait["trait_type"]: StringAttributeValue(
                        attribute_name=trait["trait_type"],
                        attribute_value=trait["value"],
                        count=trait["trait_count"],
                    )
                    for trait in token["traits"]
                }
            )

            token_obj = Token(
                token_id=token["token_id"],
                token_standard=token["asset_contract"]["schema_name"],
                collection=collection,
                metadata=token_metadata,
            )

            augment_tokens_batch.append(token_obj)

        rarity_tokens = rarity_resolver.resolve_rank(
            collection=collection, tokens=augment_tokens_batch
        )

        tokens.extend(rarity_tokens)

        batch_id = batch_id + 1

    t1_stop = process_time()
    logger.debug(
        "Elapsed time during the asset resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return tokens


def resolve_collection_data():
    """Resolves onchain collection information through OpenSea API"""

    golden_collections = pkgutil.get_data(
        "openrarity.data", "test_collections.json"
    )

    collections: list[Collection] = []

    if golden_collections:
        data = json.load(io.BytesIO(golden_collections))

        # TODO impreso@ parallalize across multiple collections
        for collection_def in data:
            tokens: list[Token] = []
            slug = collection_def["collection_slug"]
            collection = get_collection_metadata(
                collection_slug=slug, tokens=tokens
            )
            tokens.extend(get_assets(collection=collection))
            collections.append(collection)

            # TODO impreso@ serialization to file code here
    else:
        raise Exception("Can't resolve golden collections data file.")


if __name__ == "__main__":
    logger = logging.getLogger("testset_resolver")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(strftime("testsetresolverlog_%H_%M_%m_%d_%Y.log"))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    resolve_collection_data()
