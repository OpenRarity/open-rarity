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
from open_rarity.models.token_rarity import TokenRarity
from open_rarity.rarity_ranker import RarityRanker
from open_rarity.resolver.models.collection_with_metadata import (
    CollectionWithMetadata,
)
from open_rarity.resolver.models.token_with_rarity_data import (
    RankProvider,
    RarityData,
    TokenWithRarityData,
)
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_with_metadata_from_opensea,
    get_tokens_from_opensea,
)
from open_rarity.resolver.rarity_providers.external_rarity_provider import (
    ExternalRarityProvider,
)
from open_rarity.scoring.handlers.arithmetic_mean_scoring_handler import (
    ArithmeticMeanScoringHandler,
)
from open_rarity.scoring.handlers.geometric_mean_scoring_handler import (
    GeometricMeanScoringHandler,
)
from open_rarity.scoring.handlers.harmonic_mean_scoring_handler import (
    HarmonicMeanScoringHandler,
)
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from open_rarity.scoring.handlers.sum_scoring_handler import SumScoringHandler

harmonic_handler = HarmonicMeanScoringHandler()
arithmetic_handler = ArithmeticMeanScoringHandler()
geometric_handler = GeometricMeanScoringHandler()
sum_handler = SumScoringHandler()
ic_handler = InformationContentScoringHandler()

RankScore = tuple[int, float]
# Token ID -> Score
ScoredTokens = dict[int, float]
# Token ID -> Rank + Score
RankedTokens = dict[int, RankScore]

logger = logging.getLogger("open_rarity_logger")


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
    max_tokens_to_calculate: int = None,
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
    max_tokens_to_calculate (int, optional): If specified only gets ranking
        data of first `max_tokens`. Defaults to None.

    Returns
    -------
    list[TokenWithRarityData]
        provide list of tokens augmented with assets metadata and ranking provider
    """
    slug = collection_with_metadata.opensea_slug
    external_rarity_provider = ExternalRarityProvider()
    total_supply = min(
        max_tokens_to_calculate or collection_with_metadata.token_total_supply,
        collection_with_metadata.token_total_supply,
    )
    num_batches = math.ceil(total_supply / batch_size)
    initial_token_id = 0
    tokens_with_rarity: list[TokenWithRarityData] = []

    # Returns a list of `batch_size` token IDs, such that no token ID
    # can exceed `max_token_id` (in which case len(return_value) < `batch_size`)
    def get_token_ids(
        batch_id: int, max_token_id: int = total_supply - 1
    ) -> list[int]:
        token_id_start = initial_token_id + (batch_id * batch_size)
        token_id_end = int(min(token_id_start + batch_size - 1, max_token_id))
        return [
            token_id for token_id in range(token_id_start, token_id_end + 1)
        ]

    t1_start = process_time()
    for batch_id in range(num_batches):
        token_ids = get_token_ids(batch_id)
        logger.debug(
            f"Starting batch {batch_id} for collection "
            f"{slug}: Processing {len(token_ids)} tokens"
        )

        tokens = get_tokens_from_opensea(
            opensea_slug=collection_with_metadata.opensea_slug,
            token_ids=token_ids,
        )

        # We will store all rarities calculated across providers in this list
        tokens_rarity_batch = [
            TokenWithRarityData(token=t, rarities=[]) for t in tokens
        ]

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


def resolve_collection_data(
    resolve_remote_rarity: bool,
    package_path: str = "open_rarity.data",
    filename: str = "test_collections.json",
    max_tokens_to_calculate: int = None,
) -> None:
    """Resolves collection information through OpenSea API

    Parameters
    ----------
    resolve_remote_rarity : bool
        Set to true to resolve external rarity ranks for rank comparisons
    package_path : str, optional
        The package path for where the collection data to resolve collection data lives,
        by default "open_rarity.data"
    filename : str, optional
        The filename of the file holding the collection slugs to resolve,
        by default "test_collections.json"
    max_tokens_to_calculate : int, optional
        If specified only gets ranking data of first `max_tokens`, by default None.
        Note: If this is provided, we cannot calculate OpenRarity ranks since
        it must be calculated after calculating scoring for entire collection.

    Raises
    ------
    ValueError
        If the file containing collection slugs to resolve does not exist.
    """
    golden_collections = pkgutil.get_data(package_path, filename)
    if not golden_collections:
        raise ValueError("Can't resolve golden collections data file.")

    data = json.load(io.BytesIO(golden_collections))
    for collection_def in data:
        opensea_slug = collection_def["collection_slug"]
        # Fetch collection metadata and tokens that belong to this collection
        # from opensea and other external api's.
        collection_with_metadata = get_collection_with_metadata_from_opensea(
            opensea_collection_slug=opensea_slug
        )
        tokens_with_rarity: list[TokenWithRarityData] = get_tokens_with_rarity(
            collection_with_metadata=collection_with_metadata,
            resolve_remote_rarity=resolve_remote_rarity,
            max_tokens_to_calculate=max_tokens_to_calculate,
        )
        old_collection = collection_with_metadata.collection
        collection_with_metadata.collection = Collection(
            attributes_frequency_counts=old_collection.attributes_frequency_counts,
            tokens=[tr.token for tr in tokens_with_rarity],
        )
        collection = collection_with_metadata.collection

        if max_tokens_to_calculate is None:
            assert collection.token_total_supply == len(tokens_with_rarity)
        else:
            assert max_tokens_to_calculate == len(tokens_with_rarity)

        # Calculate and append open rarity scores
        if max_tokens_to_calculate is None:
            open_rarity_scores = resolve_open_rarity_score(
                collection, collection.tokens
            )
            augment_with_open_rarity_scores(
                tokens_with_rarity=tokens_with_rarity,
                scores=open_rarity_scores,
            )

        serialize_to_csv(
            collection_with_metadata=collection_with_metadata,
            tokens_with_rarity=tokens_with_rarity,
        )


def augment_with_open_rarity_scores(
    tokens_with_rarity: list[TokenWithRarityData], scores: OpenRarityScores
) -> None:
    """Augments tokens_with_rarity with ranks and scores computed by
    OpenRarity scorers'"""
    for token_with_rarity in tokens_with_rarity:
        token_id = token_with_rarity.token.token_identifier.token_id  # type: ignore

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


def extract_rank(tokens_to_score: dict[int, TokenRarity]) -> RankedTokens:
    """Sorts dictionary by float score and extract rank according to the score

    Parameters
    ----------
    token_id_to_scores : dict[int, TokenRarity]
        dictionary of token_id_to_scores with token_id to score mapping

    Returns
    -------
    dict[int, RankScore]
        dictionary of token to rank, score pair
    """
    ranked_tokens: list[TokenRarity] = RarityRanker.set_rarity_ranks(
        token_rarities=tokens_to_score.values()
    )
    return {
        int(token.token.token_identifier.token_id): (
            token.rank,
            token.score,
        )
        for token in ranked_tokens
    }


def resolve_open_rarity_score(
    collection: Collection, tokens: list[Token]
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

    # Dictionaries of token IDs to their respective TokenRarity for each strategy
    arthimetic_dict: dict[str, TokenRarity] = {}
    geometric_dict: dict[str, TokenRarity] = {}
    harmonic_dict: dict[str, TokenRarity] = {}
    sum_dict: dict[str, TokenRarity] = {}
    ic_dict: dict[str, TokenRarity] = {}

    logger.debug("OpenRarity scoring")

    for token in tokens:
        token_identifier = token.token_identifier
        assert isinstance(token_identifier, EVMContractTokenIdentifier)
        token_id = str(token_identifier.token_id)

        try:
            harmonic_dict[token_id] = TokenRarity(
                token=token,
                score=harmonic_handler.score_token(
                    collection=collection, token=token
                ),
            )
            arthimetic_dict[token_id] = TokenRarity(
                token=token,
                score=arithmetic_handler.score_token(
                    collection=collection, token=token
                ),
            )
            geometric_dict[token_id] = TokenRarity(
                token=token,
                score=geometric_handler.score_token(
                    collection=collection, token=token
                ),
            )
            sum_dict[token_id] = TokenRarity(
                token=token,
                score=sum_handler.score_token(
                    collection=collection, token=token
                ),
            )
            ic_dict[token_id] = TokenRarity(
                token=token,
                score=ic_handler.score_token(
                    collection=collection, token=token
                ),
            )

        except Exception:
            logger.exception(f"Can't score token {token} with OpenRarity")

    # Calculate ranks of all assets given the scores
    arthimetic_ranked_tokens = extract_rank(arthimetic_dict)
    geometric_ranked_tokens = extract_rank(geometric_dict)
    harmonic_ranked_tokens = extract_rank(harmonic_dict)
    sum_ranked_tokens = extract_rank(sum_dict)
    ic_ranked_tokens = extract_rank(ic_dict)

    t1_stop = process_time()
    logger.debug(
        "OpenRarity scores resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return OpenRarityScores(
        arithmetic_scores=arthimetic_ranked_tokens,
        geometric_scores=geometric_ranked_tokens,
        harmonic_scores=harmonic_ranked_tokens,
        sum_scores=sum_ranked_tokens,
        information_content_scores=ic_ranked_tokens,
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
) -> None:
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
