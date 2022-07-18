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
from openrarity.scoring.sum import SumRarity

OS_COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
OS_ASSETS_URL = "https://api.opensea.io/api/v1/assets"

HEADERS = {
    "Accept": "application/json",
    "X-API-KEY": "",
}


harmonic = HarmonicMeanRarity()
arithmetic = ArithmeticMeanRarity()
geometric = GeometricMeanRarity()
sum = SumRarity()

RankScore = tuple[int, float]
ScorredTokens = dict[int, float]
RankedTokens = dict[int, RankScore]
OpenRarityScores = tuple[
    RankedTokens, RankedTokens, RankedTokens, RankedTokens
]


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
    collection: Collection, resolve_remote_rarity: bool = True
) -> list[Token]:
    """Resolves assets through OpenSea API asset endpoint.
        Augment metadata with Gem rankings from Gem, RaritySniper and TraitSniper.

    Parameters
    ----------
    collection : Collection
        collection
    resolve_remote_rarity : bool
        True if we need to resolve rarity ranks from
        external providers , False if not

    Returns
    -------
    list[Token]
        provide list of tokens augmented with assets metadata and ranking provider
    """
    rarity_resolver = ExternalRarityProvider()
    batch_id = 0
    # TODO impreso@ handle the case with collections where mod 30 !=0
    range_end = int(collection.token_total_supply / 30)
    # range_end = 4
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
        if resolve_remote_rarity:
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
                    collection=collection, resolve_remote_rarity=resolve_remote
                )
            )

            open_rarity_ranks = resolve_open_rarity_score(
                collection=collection, normalized=True
            )

            augment_with_or_rank(
                collection=collection, or_ranks=open_rarity_ranks
            )

            collection_to_csv(collection=collection)

    else:
        raise Exception("Can't resolve golden collections data file.")


def augment_with_or_rank(collection: Collection, or_ranks: OpenRarityScores):
    """Augments collection tokens with ranks computed by OpenRarity scorrer

    Parameters
    ----------
    collection : Collection
        collection
    or_ranks : OpenRarityScores
        ranks
    """

    arithm = or_ranks[0]
    geom = or_ranks[1]
    harm = or_ranks[2]
    sum = or_ranks[3]

    for token in collection.tokens:
        try:
            token.ranks.append(
                (RankProvider.OR_ARITHMETIC, arithm[token.token_id][0])
            )
            token.ranks.append(
                (RankProvider.OR_GEOMETRIC, geom[token.token_id][0])
            )
            token.ranks.append(
                (RankProvider.OR_HARMONIC, harm[token.token_id][0])
            )
            token.ranks.append((RankProvider.OR_SUM, sum[token.token_id][0]))
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
        dictionary of scores with token_id to score mapping

    Returns
    -------
    dict[int, RankScore]
        dictionary of token to rank, score pair
    """
    srt = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))  # type: ignore

    res = {}
    for index, (key, value) in enumerate(srt.items()):
        # upsacle by 1 position since index start from 0
        res[key] = (index + 1, value)

    return res


def resolve_open_rarity_score(
    collection: Collection, normalized: bool
) -> OpenRarityScores:
    """Resolve scores from all scorrers with trait_normalization

    Parameters
    ----------
    collection : Collection
        collection

    """
    t1_start = process_time()

    arthimetic_dict = {}
    geometric_dict = {}
    harmonic_dict = {}
    sum_dict = {}

    logger.debug("OpenRarity scorring")

    for token in collection.tokens:
        try:
            harmonic_dict[token.token_id] = harmonic.score_token(
                token=token, normalized=normalized
            )
            arthimetic_dict[token.token_id] = arithmetic.score_token(
                token=token, normalized=normalized
            )
            geometric_dict[token.token_id] = geometric.score_token(
                token=token, normalized=normalized
            )
            sum_dict[token.token_id] = sum.score_token(
                token=token, normalized=normalized
            )

        except Exception:
            logger.exception(
                "Can't score token {id} with OpenRarity".format(
                    id=token.token_id
                )
            )

    arthimetic_dict = extract_rank(arthimetic_dict)
    harmonic_dict = extract_rank(harmonic_dict)
    geometric_dict = extract_rank(geometric_dict)
    sum_dict = extract_rank(sum_dict)

    t1_stop = process_time()
    logger.debug(
        "OpenRarity scores resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return (arthimetic_dict, geometric_dict, harmonic_dict, sum_dict)


def __get_provider_rank(provider: RankProvider, token: Token) -> int | None:
    """Get rank for the particular provider

    Parameters
    ----------
    provider : RankProvider
        rank provider
    token : Token
        token
    """
    rank = list(filter(lambda rank: rank[0] == provider, token.ranks))
    return rank[0][1] if len(rank) > 0 else None


def __rank_diff(rank1: int | None, rank2: int | None) -> int | None:
    """Function that computes the rank difference

    Parameters
    ----------
    rank1 : int | None
        rank of the asset
    rank2 : int | None
        rank of the asset

    Returns
    -------
    int | None
        absolute difference of ranks for the specific asset
    """
    if not rank1 or not rank2:
        return None

    return abs(rank1 - rank2)


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
        "arithmetic",
        "geometric",
        "harmonic",
        "sum",
        "traits_sniper_rarity_sniffer_diff",
        "traits_sniper_arithm_diff",
        "traits_sniper_geom_diff",
        "traits_sniper_harmo_diff",
        "traits_sniper_sum_diff",
        "rarity_sniffer_arithm_diff",
        "rarity_sniffer_geom_diff",
        "rarity_sniffer_harmo_diff",
        "rarity_sniffer_sum_diff",
    ]

    writer = csv.writer(testset)
    writer.writerow(header)

    for token in collection.tokens:
        row = []
        traits_sniper_rank = __get_provider_rank(
            provider=RankProvider.TRAITS_SNIPER, token=token
        )

        rarity_sniffer_rank = __get_provider_rank(
            provider=RankProvider.RARITY_SNIFFER, token=token
        )

        or_arithmetic_rank = __get_provider_rank(
            provider=RankProvider.OR_ARITHMETIC, token=token
        )

        or_geometric_rank = __get_provider_rank(
            provider=RankProvider.OR_GEOMETRIC, token=token
        )

        or_harmonic_rank = __get_provider_rank(
            provider=RankProvider.OR_HARMONIC, token=token
        )
        or_sum_rank = __get_provider_rank(
            provider=RankProvider.OR_SUM, token=token
        )

        row.append(collection.slug)
        row.append(token.token_id)
        row.append(traits_sniper_rank)
        row.append(rarity_sniffer_rank)
        row.append(or_arithmetic_rank)
        row.append(or_geometric_rank)
        row.append(or_harmonic_rank)
        row.append(or_sum_rank)
        row.append(__rank_diff(traits_sniper_rank, rarity_sniffer_rank))
        row.append(__rank_diff(traits_sniper_rank, or_arithmetic_rank))
        row.append(__rank_diff(traits_sniper_rank, or_geometric_rank))
        row.append(__rank_diff(traits_sniper_rank, or_harmonic_rank))
        row.append(__rank_diff(traits_sniper_rank, or_sum_rank))
        row.append(__rank_diff(rarity_sniffer_rank, or_arithmetic_rank))
        row.append(__rank_diff(rarity_sniffer_rank, or_geometric_rank))
        row.append(__rank_diff(rarity_sniffer_rank, or_harmonic_rank))
        row.append(__rank_diff(rarity_sniffer_rank, or_sum_rank))

        writer.writerow(row)


if __name__ == "__main__":
    """Script to resolve external datasets and compute rarity scores
    on test collections. Data resolved from opensea api

    command to run: python -m  openrarity.resolver.testset_resolver external
    """

    resolve_remote_rarity = False
    print(argv)
    if len(argv) > 1:
        resolve_remote_rarity = True
    logger = logging.getLogger("open_rarity_logger")

    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(strftime("testsetresolverlog_%H_%M_%m_%d_%Y.log"))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    logger.debug(
        "Resolving external rarity {flag}".format(flag=resolve_remote_rarity)
    )

    resolve_collection_data(resolve_remote_rarity)
