import csv
import io
import json
import logging
import math
import pkgutil
from dataclasses import dataclass
from sys import argv
from time import process_time, strftime

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_standard import TokenStandard
from open_rarity.resolver.models.collection_with_metadata import (
    CollectionWithMetadata,
)
from open_rarity.resolver.models.token_with_rarity_data import (
    RankProvider,
    RarityData,
    TokenWithRarityData,
)
from open_rarity.resolver.opensea_api_helpers import (
    fetch_opensea_assets_data,
    get_collection_with_metadata,
    opensea_traits_to_token_metadata,
)
from open_rarity.resolver.rarity_providers.external_rarity_provider import (
    ExternalRarityProvider,
)
from open_rarity.scoring.scorers.arithmetic_mean_scorer import (
    ArithmeticMeanRarityScorer,
)
from open_rarity.scoring.scorers.geometric_mean_scorer import (
    GeometricMeanRarityScorer,
)
from open_rarity.scoring.scorers.harmonic_mean_scorer import (
    HarmonicMeanRarityScorer,
)
from open_rarity.scoring.scorers.information_content_scorer import (
    InformationContentRarityScorer,
)
from open_rarity.scoring.scorers.sum_scorer import SumRarityScorer

harmonic_scorer = HarmonicMeanRarityScorer()
arithmetic_scorer = ArithmeticMeanRarityScorer()
geometric_scorer = GeometricMeanRarityScorer()
sum_scorer = SumRarityScorer()
ic_scorer = InformationContentRarityScorer()

RankScore = tuple[int, float]
# Token ID -> Score
ScoredTokens = dict[int, float]
# Token ID -> Rank + Score
RankedTokens = dict[int, RankScore]


@dataclass
class OpenRarityScores:
    arithmetic_scores: RankedTokens
    geometric_scores: RankedTokens
    harmonic_scores: RankedTokens
    sum_scores: RankedTokens
    information_content_scores: RankedTokens


def get_tokens_with_rarity(
    collection_with_metadata: CollectionWithMetadata,
    resolve_remote_rarity: bool = True,
    batch_size: int = 30,
) -> list[TokenWithRarityData]:
    """Resolves assets through OpenSea API asset endpoint and turns them
    into token with rarity data, augmented with rankings from Gem, RaritySniper
    and TraitSniper.

    Parameters
    ----------
    collection : Collection
        collection
    resolve_remote_rarity : bool
        True if we need to resolve rarity ranks from
        external providers , False if not

    Returns
    -------
    list[TokenWithRarityData]
        provide list of tokens augmented with assets metadata and ranking provider
    """
    external_rarity_provider = ExternalRarityProvider()
    total_supply = collection_with_metadata.token_total_supply
    num_batches = math.ceil(total_supply / batch_size)
    initial_token_id = 1
    tokens_with_rarity: list[TokenWithRarityData] = []

    # Returns a list of `batch_size` token IDs, such that no token ID
    # can exceed `max_token_id` (in which case len(return_value) < `batch_size`)
    def get_token_ids(
        batch_id: int, max_token_id: int = total_supply
    ) -> list[int]:
        token_id_start = initial_token_id + (batch_id * batch_size)
        token_id_end = max(token_id_start + batch_size - 1, max_token_id)
        return [token_id for token_id in range(token_id_start, token_id_end)]

    t1_start = process_time()
    for batch_id in range(num_batches):
        token_ids = get_token_ids(batch_id)
        logger.debug(
            f"Starting batch {batch_id} for collection "
            f"{collection_with_metadata.opensea_slug}: "
            f"Processing {len(token_ids)} tokens"
        )

        try:
            assets = fetch_opensea_assets_data(
                slug=collection_with_metadata.opensea_slug, token_ids=token_ids
            )
        except Exception:
            print(
                f"FAILED: get_assets: could not fetch opensea assets for {token_ids}"
            )
            break

        # We will store all rarities calculated across providers in this list
        tokens_rarity_batch: list[TokenWithRarityData] = []
        for asset in assets:
            token_metadata = opensea_traits_to_token_metadata(asset["traits"])
            asset_contract_address = asset["asset_contract"]["address"]
            asset_contract_type = asset["asset_contract"][
                "asset_contract_type"
            ]
            if asset_contract_type == "non-fungible":
                token_standard = TokenStandard.ERC721
            elif asset_contract_type == "semi-fungible":
                token_standard = TokenStandard.ERC1155
            else:
                raise Exception(
                    f"Unexpected asset contrat type: {asset_contract_type}"
                )

            token_with_rarity = TokenWithRarityData(
                token=Token(
                    token_identifier=EVMContractTokenIdentifier(
                        identifier_type="evm_contract",
                        contract_address=asset_contract_address,
                        token_id=asset["token_id"],
                    ),
                    token_standard=token_standard,
                    metadata=token_metadata,
                ),
                rarities=[],
            )

            tokens_rarity_batch.append(token_with_rarity)

        if resolve_remote_rarity:
            external_rarity_provider.fetch_and_update_ranks(
                collection_with_metadata=collection_with_metadata,
                tokens_with_rarity=tokens_rarity_batch,
            )

        # Add the batch of augmented tokens with rarity into return value
        tokens_with_rarity.extend(tokens_rarity_batch)

    t1_stop = process_time()
    logger.debug(
        "Elapsed time during the asset resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return tokens_with_rarity


def resolve_collection_data(resolve_remote_rarity: bool):
    """Resolves collection information through OpenSea API"""

    golden_collections = pkgutil.get_data(
        "openrarity.data", "test_collections.json"
    )

    if golden_collections:
        data = json.load(io.BytesIO(golden_collections))
        for collection_def in data:
            opensea_slug = collection_def["collection_slug"]
            # Fetch collection metadata and tokens that belong to this collection
            # from opensea and other external api's.
            collection_with_metadata = get_collection_with_metadata(
                opensea_collection_slug=opensea_slug
            )
            tokens_with_rarity: list[
                TokenWithRarityData
            ] = get_tokens_with_rarity(
                collection_with_metadata=collection_with_metadata,
                resolve_remote_rarity=resolve_remote_rarity,
            )
            collection = collection_with_metadata.collection
            collection.tokens = [tr.token for tr in tokens_with_rarity]
            assert collection.token_total_supply == len(tokens_with_rarity)

            # Calculate and append open rarity scores
            open_rarity_scores = resolve_open_rarity_score(
                collection, collection.tokens, normalized=True
            )
            augment_with_open_rarity_scores(
                tokens_with_rarity=tokens_with_rarity,
                scores=open_rarity_scores,
            )

            serialize_to_csv(
                collection_with_metadata=collection_with_metadata,
                tokens_with_rarity=tokens_with_rarity,
            )

    else:
        raise Exception("Can't resolve golden collections data file.")


def augment_with_open_rarity_scores(
    tokens_with_rarity: list[TokenWithRarityData], scores: OpenRarityScores
):
    """Augments tokens_with_rarity with ranks and scores computed by
    OpenRarity scorers'"""
    for token_with_rarity in tokens_with_rarity:
        token_id = token_with_rarity.token.token_identifier.token_id  # type: ignore
        try:
            token_with_rarity.rarities.extend(
                [
                    RarityData(
                        provider=RankProvider.OR_ARITHMETIC,
                        rank=scores.arithmetic_scores[token_id][0],
                        score=scores.arithmetic_scores[token_id][1],
                    ),
                    RarityData(
                        provider=RankProvider.OR_GEOMETRIC,
                        rank=scores.geometric_scores[token_id][0],
                        score=scores.geometric_scores[token_id][1],
                    ),
                    RarityData(
                        provider=RankProvider.OR_HARMONIC,
                        rank=scores.harmonic_scores[token_id][0],
                        score=scores.harmonic_scores[token_id][1],
                    ),
                    RarityData(
                        provider=RankProvider.OR_SUM,
                        rank=scores.sum_scores[token_id][0],
                        score=scores.sum_scores[token_id][1],
                    ),
                    RarityData(
                        provider=RankProvider.OR_INFORMATION_CONTENT,
                        rank=scores.information_content_scores[token_id][0],
                        score=scores.information_content_scores[token_id][1],
                    ),
                ]
            )
        except Exception:
            logger.exception(
                f"Error occured with OR rank calc for token {token_with_rarity.token}"
            )


def extract_rank(token_id_to_scores: ScoredTokens) -> RankedTokens:
    """Sorts dictionary by float score and extract rank according to the score

    Parameters
    ----------
    token_id_to_scores : dict
        dictionary of token_id_to_scores with token_id to score mapping

    Returns
    -------
    dict[int, RankScore]
        dictionary of token to rank, score pair
    """
    srt = dict(
        sorted(token_id_to_scores.items(), key=lambda x: x[1], reverse=True)
    )

    res = {}
    for index, (key, value) in enumerate(srt.items()):
        # upsacle by 1 position since index start from 0
        res[key] = (index + 1, value)

    return res


def resolve_open_rarity_score(
    collection: Collection, tokens: list[Token], normalized: bool
) -> OpenRarityScores:
    """Resolve scores from all scorers with trait_normalization

    Parameters
    ----------
    collection : Collection
        collection is needed since the score is based on the invdividual's traits
        probability across the entire collection
    tokens: Subset of tokens belonging to Collection to resolve open rarity scores for

    """
    t1_start = process_time()

    # Dictionaries of token IDs to their respective score for each strategy
    arthimetic_dict = {}
    geometric_dict = {}
    harmonic_dict = {}
    sum_dict = {}
    ic_dict = {}

    logger.debug("OpenRarity scoring")

    for token in tokens:
        token_identifier = token.token_identifier
        assert isinstance(token_identifier, EVMContractTokenIdentifier)
        token_id = token_identifier.token_id

        try:
            harmonic_dict[token_id] = harmonic_scorer.score_token(
                collection=collection, token=token, normalized=normalized
            )
            arthimetic_dict[token_id] = arithmetic_scorer.score_token(
                collection=collection, token=token, normalized=normalized
            )
            geometric_dict[token_id] = geometric_scorer.score_token(
                collection=collection, token=token, normalized=normalized
            )
            sum_dict[token_id] = sum_scorer.score_token(
                collection=collection, token=token, normalized=normalized
            )
            ic_dict[token_id] = ic_scorer.score_token(
                collection=collection, token=token, normalized=normalized
            )

        except Exception:
            logger.exception(f"Can't score token {token} with OpenRarity")

    # Calculate ranks of all assets given the scores
    arthimetic_dict = extract_rank(arthimetic_dict)
    geometric_dict = extract_rank(geometric_dict)
    harmonic_dict = extract_rank(harmonic_dict)
    sum_dict = extract_rank(sum_dict)
    ic_dict = extract_rank(ic_dict)

    t1_stop = process_time()
    logger.debug(
        "OpenRarity scores resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return OpenRarityScores(
        arithmetic_scores=arthimetic_dict,
        geometric_scores=geometric_dict,
        harmonic_scores=harmonic_dict,
        sum_scores=sum_dict,
        information_content_scores=ic_dict,
    )


def _get_provider_rank(
    provider: RankProvider, token_with_rarity: TokenWithRarityData
) -> int | None:
    """Get rank for the particular provider

    Parameters
    ----------
    provider : RankProvider
        rank provider
    token : Token
        token
    """
    rarities = token_with_rarity.rarities
    rarity_datas = list(
        filter(lambda rarity: rarity.provider == provider, rarities)
    )
    return rarity_datas[0].rank if len(rarity_datas) > 0 else None


def _rank_diff(rank1: int | None, rank2: int | None) -> int | None:
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


def serialize_to_csv(
    collection_with_metadata: CollectionWithMetadata,
    tokens_with_rarity: list[TokenWithRarityData],
):
    """Serialize collection and ranking data to CSV

    Parameters
    ----------
    collection : Collection
        collection
    """
    slug = collection_with_metadata.opensea_slug
    testset = open(f"testset_{slug}.csv", "w")
    headers = [
        "slug",
        "token_id",
        "traits_sniper",
        "rarity_sniffer",
        "rarity_sniper",
        "arithmetic",
        "geometric",
        "harmonic",
        "sum",
        "information_content",
        "traits_sniper_rarity_sniffer_diff",
        "traits_sniper_rarity_sniper_diff",
        "traits_sniper_arithm_diff",
        "traits_sniper_geom_diff",
        "traits_sniper_harmo_diff",
        "traits_sniper_sum_diff",
        "traits_sniper_ic_diff",
        "rarity_sniffer_rarity_sniper_diff",
        "rarity_sniffer_arithm_diff",
        "rarity_sniffer_geom_diff",
        "rarity_sniffer_harmo_diff",
        "rarity_sniffer_sum_diff",
        "rarity_sniffer_ic_diff",
        "rarity_sniper_arithm_diff",
        "rarity_sniper_geom_diff",
        "rarity_sniper_harmo_diff",
        "rarity_sniper_sum_diff",
        "rarity_sniper_ic_diff",
    ]

    writer = csv.writer(testset)
    writer.writerow(headers)

    for token_with_rarity in tokens_with_rarity:
        traits_sniper_rank = _get_provider_rank(
            RankProvider.TRAITS_SNIPER, token_with_rarity
        )
        rarity_sniffer_rank = _get_provider_rank(
            RankProvider.RARITY_SNIFFER, token_with_rarity
        )
        rarity_sniper_rank = _get_provider_rank(
            RankProvider.RARITY_SNIPER, token_with_rarity
        )
        or_arithmetic_rank = _get_provider_rank(
            RankProvider.OR_ARITHMETIC, token_with_rarity
        )
        or_geometric_rank = _get_provider_rank(
            RankProvider.OR_GEOMETRIC, token_with_rarity
        )
        or_harmonic_rank = _get_provider_rank(
            RankProvider.OR_HARMONIC, token_with_rarity
        )
        or_sum_rank = _get_provider_rank(
            RankProvider.OR_SUM, token_with_rarity
        )
        or_ic_rank = _get_provider_rank(
            RankProvider.OR_INFORMATION_CONTENT, token_with_rarity
        )
        row = [
            slug,
            token_with_rarity.token.token_identifier.token_id,  # type: ignore
            traits_sniper_rank,
            rarity_sniffer_rank,
            rarity_sniper_rank,
            or_arithmetic_rank,
            or_geometric_rank,
            or_harmonic_rank,
            or_sum_rank,
            or_ic_rank,
            _rank_diff(traits_sniper_rank, rarity_sniffer_rank),
            _rank_diff(traits_sniper_rank, rarity_sniper_rank),
            _rank_diff(traits_sniper_rank, or_arithmetic_rank),
            _rank_diff(traits_sniper_rank, or_geometric_rank),
            _rank_diff(traits_sniper_rank, or_harmonic_rank),
            _rank_diff(traits_sniper_rank, or_sum_rank),
            _rank_diff(traits_sniper_rank, or_ic_rank),
            _rank_diff(rarity_sniffer_rank, rarity_sniper_rank),
            _rank_diff(rarity_sniffer_rank, or_arithmetic_rank),
            _rank_diff(rarity_sniffer_rank, or_geometric_rank),
            _rank_diff(rarity_sniffer_rank, or_harmonic_rank),
            _rank_diff(rarity_sniffer_rank, or_sum_rank),
            _rank_diff(rarity_sniffer_rank, or_ic_rank),
            _rank_diff(rarity_sniper_rank, or_arithmetic_rank),
            _rank_diff(rarity_sniper_rank, or_geometric_rank),
            _rank_diff(rarity_sniper_rank, or_harmonic_rank),
            _rank_diff(rarity_sniper_rank, or_sum_rank),
            _rank_diff(rarity_sniper_rank, or_ic_rank),
        ]
        writer.writerow(row)


if __name__ == "__main__":
    """Script to resolve external datasets and compute rarity scores
    on test collections. Data resolved from opensea api

    command to run: python -m  openrarity.resolver.testset_resolver external
    """

    resolve_remote_rarity = len(argv) > 1
    print(f"Executing main: with {argv}. Setting {resolve_remote_rarity=}")

    logger = logging.getLogger("open_rarity_logger")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(strftime("testsetresolverlog_%H_%M_%m_%d_%Y.log"))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    resolve_collection_data(resolve_remote_rarity)
