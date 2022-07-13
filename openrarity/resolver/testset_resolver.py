import io
import json
import pkgutil
from sys import argv
from time import process_time

import requests

from openrarity.models.collection import Collection
from openrarity.models.chain import Chain
from openrarity.models.token import RankProvider, Token
from openrarity.models.token_metadata import (
    StringAttributeValue,
    TokenMetadata,
)
from openrarity.resolver.rarity_providers.rarity_provider import (
    ExternalRarityProvider,
)
import logging
from time import strftime
import csv
from openrarity.scoring.arithmetic_mean import ArithmeticMeanRarity
from openrarity.scoring.geometric_mean import GeometricMeanRarity

from openrarity.scoring.harmonic_mean import HarmonicMeanRarity

OS_COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
OS_ASSETS_URL = "https://api.opensea.io/api/v1/assets"

HEADERS = {
    "Accept": "application/json",
    "X-API-KEY": "",
}


harmonic = HarmonicMeanRarity()
arithmetic = ArithmeticMeanRarity()
geometric = GeometricMeanRarity()

RankScore = tuple[int, float]
RarityScore = float
ScorredTokens = dict[int, RarityScore]
RankedTokens = dict[int, RankScore]
OpenRartityScores = tuple[RankedTokens, RankedTokens, RankedTokens]


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


def get_assets(
    collection: Collection, resolve_rarity: bool = True
) -> list[Token]:
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
    # range_end = 1
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
            "limit": 30,
        }

        response = requests.request(
            "GET",
            OS_ASSETS_URL,
            headers=HEADERS,
            params=querystring,
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

        rarity_tokens = augment_tokens_batch
        if resolve_rarity:
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


def resolve_collection_data(resolve_remote: bool):
    """Resolves onchain collection information through OpenSea API"""

    golden_collections = pkgutil.get_data(
        "openrarity.data", "test_collections.json"
    )

    if golden_collections:
        data = json.load(io.BytesIO(golden_collections))
        for collection_def in data:
            tokens: list[Token] = []
            slug = collection_def["collection_slug"]
            collection = get_collection_metadata(
                collection_slug=slug, tokens=tokens
            )
            tokens.extend(
                get_assets(
                    collection=collection, resolve_rarity=resolve_remote
                )
            )

            open_rarity_ranks = resolve_open_rarity_score(
                collection=collection
            )

            augment_with_or_rank(
                collection=collection, or_ranks=open_rarity_ranks
            )

            collection_to_csv(collection=collection)

    else:
        raise Exception("Can't resolve golden collections data file.")


def augment_with_or_rank(collection: Collection, or_ranks: OpenRartityScores):
    """Augments collection tokens with ranks computed by OpenRarity scorrer

    Parameters
    ----------
    collection : Collection
        _description_
    or_ranks : OpenRartityScores
        _description_
    """

    ariphm = or_ranks[0]
    geom = or_ranks[1]
    harm = or_ranks[2]

    for token in collection.tokens:
        try:
            token.ranks.append(
                (RankProvider.OR_ARITHMETIC, ariphm[token.token_id][0])
            )
            token.ranks.append(
                (RankProvider.OR_GEOMETRIC, geom[token.token_id][0])
            )
            token.ranks.append(
                (RankProvider.OR_HARMONIC, harm[token.token_id][0])
            )
        except Exception:
            logger.exception(
                "Error occured during OR rank resolution for token {id}".format(
                    id=token.token_id
                )
            )


def extract_rank(scores: ScorredTokens) -> RankedTokens:
    """Sorts dictionary by float score and extract rank according to the score

    Parameters
    ----------
    scores : dict
        _description_

    Returns
    -------
    dict[int, RankScore]
        _description_
    """
    srt = dict(sorted(scores.items(), key=lambda item: item[1]))  # type: ignore

    res = {}
    for index, (key, value) in enumerate(srt.items()):
        res[key] = (index, value)

    logger.debug(res)

    return res


def resolve_open_rarity_score(
    collection: Collection,
) -> OpenRartityScores:
    """Resolve scores from all scorrers with trait_normalization

    Parameters
    ----------
    collection : Collection
        collection

    Returns
    -------
    _type_
        _description_
    """
    arphimetic_dict = {}
    geometric_dict = {}
    harmonic_dict = {}

    logger.debug("OpenRarity scorring")

    for token in collection.tokens:
        try:
            harmonic_dict[token.token_id] = harmonic.score_token(token=token)
            arphimetic_dict[token.token_id] = arithmetic.score_token(
                token=token
            )
            geometric_dict[token.token_id] = geometric.score_token(token=token)

        except Exception:
            logger.exception(
                "Can't score token {id} with OpenRarity".format(
                    id=token.token_id
                )
            )

    arphimetic_dict = extract_rank(arphimetic_dict)
    harmonic_dict = extract_rank(harmonic_dict)
    geometric_dict = extract_rank(geometric_dict)

    return (arphimetic_dict, geometric_dict, harmonic_dict)


def collection_to_csv(collection: Collection):
    """Serialize collection to CSV

    Parameters
    ----------
    collection : Collection
        collection
    """
    testset = open(
        "testset_{slug}.csv".format(slug=collection.slug),
        "w",
    )
    header = [
        "slug",
        "token_id",
        "traits_sniper",
        "rarity_sniffer",
        "ariphmetic",
        "geometric",
        "harmonic",
    ]

    writer = csv.writer(testset)
    writer.writerow(header)

    for token in collection.tokens:
        row = []
        traits_sniper_rank = list(
            filter(
                lambda rank: rank[0] == RankProvider.TRAITS_SNIPER, token.ranks
            )
        )

        rarity_sniffer_rank = list(
            filter(
                lambda rank: rank[0] == RankProvider.RARITY_SNIFFER,
                token.ranks,
            )
        )

        or_ariphmetic_rank = list(
            filter(
                lambda rank: rank[0] == RankProvider.OR_ARITHMETIC,
                token.ranks,
            )
        )

        or_geometric_rank = list(
            filter(
                lambda rank: rank[0] == RankProvider.OR_GEOMETRIC,
                token.ranks,
            )
        )

        or_harominc_rank = list(
            filter(
                lambda rank: rank[0] == RankProvider.OR_HARMONIC,
                token.ranks,
            )
        )

        row.append(collection.slug)
        row.append(token.token_id)
        row.append(
            traits_sniper_rank[0][1] if len(traits_sniper_rank) > 0 else None
        )
        row.append(
            rarity_sniffer_rank[0][1] if len(rarity_sniffer_rank) > 0 else None
        )
        row.append(
            or_ariphmetic_rank[0][1] if len(or_ariphmetic_rank) > 0 else None
        )
        row.append(
            or_geometric_rank[0][1] if len(or_geometric_rank) > 0 else None
        )
        row.append(
            or_harominc_rank[0][1] if len(or_harominc_rank) > 0 else None
        )

        writer.writerow(row)


if __name__ == "__main__":
    """Script to resolve external datasets and compute rarity scores
    on test collections. Data resolved from opensea api"""

    resolve_remote = False
    if len(argv) > 2:
        resolve_remote = True
    logger = logging.getLogger("testset_resolver")

    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(strftime("testsetresolverlog_%H_%M_%m_%d_%Y.log"))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    logger.debug(
        "Resolving external rarity {flag}".format(flag=resolve_remote)
    )

    resolve_collection_data(resolve_remote)
