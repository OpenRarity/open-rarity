import json
import logging
from collections import defaultdict

from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.resolver.models.collection_with_metadata import CollectionWithMetadata
from open_rarity.resolver.models.token_with_rarity_data import (
    EXTERNAL_RANK_PROVIDERS,
    RankProvider,
    RarityData,
    TokenWithRarityData,
)

from .rank_resolver import RankResolver
from .rarity_sniffer import RaritySnifferResolver
from .rarity_sniper import RaritySniperResolver
from .trait_sniper import TraitSniperResolver

logger = logging.getLogger("open_rarity_logger")


def get_external_resolver(rank_provider: RankProvider) -> RankResolver:
    if rank_provider == RankProvider.TRAITS_SNIPER:
        return TraitSniperResolver()
    elif rank_provider == RankProvider.RARITY_SNIFFER:
        return RaritySnifferResolver()
    elif rank_provider == RankProvider.RARITY_SNIPER:
        return RaritySniperResolver()
    raise Exception(f"Unknown external rank provider: {rank_provider}")


class ExternalRarityProvider:
    # Cached file will have format:
    # "{collection_slug}_{provider_name}_cached_ranks.json"
    # The data must be a dictionary of <token id as int> to <rank as int>
    CACHE_FILENAME_FORMAT: str = "cached_data/%s_%s_cached_ranks.json"

    # Dictionary of slug -> {token_id (str) -> rank (int)}
    _trait_sniper_cache: dict[str, dict[str, int]] = defaultdict(dict)
    _rarity_sniffer_cache: dict[str, dict[str, int]] = defaultdict(dict)
    _rarity_sniper_cache: dict[str, dict[str, int]] = defaultdict(dict)

    def cache_filename(self, rank_provider: RankProvider, slug: str) -> str:
        rank_name = rank_provider.name.lower()
        return self.CACHE_FILENAME_FORMAT % (slug, rank_name)

    def fetch_and_update_ranks(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        rank_providers: list[RankProvider] = EXTERNAL_RANK_PROVIDERS,
        cache_external_ranks: bool = True,
    ) -> list[TokenWithRarityData]:
        """Fetches ranks from available providers gem, rarity sniper and/or trait sniper
        and adds them to the rarities field in `tokens_with_rarity`

        Parameters
        ----------
        collection : Collection
            collection
        tokens_with_rarity: list[TokenWithRaritydata]
            List of tokens with rarity data. Will modify the objects.rarities
            field and add the fetched ranking data directly to object.
        cache_external_ranks: bool
            If set to true, will use local cache file instead of fetching rank data.
            If cache is empty, will fetch data from API and write to local cache.

        Returns
        -------
        list[tokens_with_rarity]
            tokens with fetched external rarity data
        """
        logger.debug(f"Fetching external rarity for {len(tokens_with_rarity)} tokens")

        for rank_provider in rank_providers:
            # Note: Not all providers have rankings for all collections,
            # so do a best effort.
            print("\t\tProcessing provider: ", rank_provider)
            try:
                if rank_provider in {
                    RankProvider.RARITY_SNIFFER,
                    RankProvider.TRAITS_SNIPER,
                }:
                    self._add_rarity_data(
                        rank_provider=rank_provider,
                        collection_with_metadata=collection_with_metadata,
                        tokens_with_rarity=tokens_with_rarity,
                        cache_external_ranks=cache_external_ranks,
                    )
                elif rank_provider == RankProvider.RARITY_SNIPER:
                    self._add_rarity_sniper_rarity_data(
                        collection_with_metadata=collection_with_metadata,
                        tokens_with_rarity=tokens_with_rarity,
                        cache_external_ranks=cache_external_ranks,
                    )
            except Exception:
                logger.exception(
                    f"Exception: Could not get ranks from {rank_provider} for "
                    f"{collection_with_metadata.opensea_slug}",
                    exc_info=True,
                )
                continue
        return tokens_with_rarity

    # Private methods
    def _add_rarity_data(
        self,
        rank_provider: RankProvider,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        cache_external_ranks: bool = True,
    ) -> list[TokenWithRarityData]:
        """Modifies `tokens_with_rarity` by adding external provider rank data
        Currently only works for EVM collections

        Parameters
        ----------
        collection_with_metadata : CollectionWithMetadata
        tokens_with_rarity : list[TokenWithRarityData]
            list of tokens with rarity to augment

        Returns
        -------
        list[TokenWithRarityData]
            list of augmeneted tokens
        """
        slug = collection_with_metadata.opensea_slug
        logger.debug(f"Resolving {rank_provider} data for {slug}")
        contract_addresses = collection_with_metadata.contract_addresses
        if len(contract_addresses) != 1:
            raise ValueError(
                f"We cannot calculate {rank_provider.value} score for collections "
                f"that do not map to a single contract address: {contract_addresses=}"
            )
        contract_address = contract_addresses[0]

        # Get input params and validate
        if rank_provider == RankProvider.RARITY_SNIPER:
            raise ValueError(
                "Invalid rank provider. Needs to support bulk rank fetching first."
            )

        # Load data from local cache if available
        if cache_external_ranks:
            self._load_cache_from_file(slug=slug, rank_provider=rank_provider)

        # If we didn't want to load cache or cache is empty, pull data from API
        if not self._is_cache_loaded(slug, rank_provider):
            resolver = get_external_resolver(rank_provider)
            token_ids_to_ranks = resolver.get_all_ranks(contract_address)
            self._set_cache(
                slug=slug, rank_provider=rank_provider, rank_data=token_ids_to_ranks
            )
            num_tokens = len(token_ids_to_ranks)
            logger.debug(
                f"Fetched {num_tokens} ranks from {rank_provider} API and cached"
            )
            if not token_ids_to_ranks:
                logger.warning(f"Did not get any data for {slug} from {rank_provider}")
                raise Exception(
                    f"Could not get data from external rank provider: {rank_provider}"
                )
            if cache_external_ranks:
                self.write_cache_to_file(slug, rank_provider)

        # Fill in ranks for each token
        for token_with_rarity in tokens_with_rarity:
            token_identifer = token_with_rarity.token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id

            rank = self._get_cached_rank(
                slug=slug, rank_provider=rank_provider, token_id=token_id
            )

            if rank:
                token_with_rarity.rarities.append(
                    RarityData(provider=rank_provider, rank=rank)
                )

        return tokens_with_rarity

    def _add_rarity_sniper_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        cache_external_ranks: bool = True,
    ) -> list[TokenWithRarityData]:
        # We're currently using opensea slug to calculate trait sniper slug
        opensea_slug = collection_with_metadata.opensea_slug
        slug = RaritySniperResolver.get_slug(opensea_slug=opensea_slug)
        rank_provider = RankProvider.RARITY_SNIPER
        if cache_external_ranks:
            self._load_cache_from_file(slug=opensea_slug, rank_provider=rank_provider)

        for token_with_rarity in tokens_with_rarity:
            token = token_with_rarity.token
            token_identifer = token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id
            rank = self._get_cached_rank(
                slug=opensea_slug,
                rank_provider=rank_provider,
                token_id=token_id,
            )

            if rank is None:
                try:
                    rank = RaritySniperResolver.get_rank(
                        collection_slug=slug, token_id=token_id
                    )
                    print(
                        f"[RaritySniper] Fetched from api: {rank=} {token_id=} {slug=}"
                    )
                    logger.debug(
                        "Resolved rarity sniper rarity for "
                        f"{opensea_slug=}/{slug=} {token_id=}: {rank}"
                    )
                except Exception:
                    logger.exception(
                        "[Rarity Sniper] Failed to resolve from API:"
                        f"{opensea_slug=}/{slug=} {token_id=}: {rank}",
                        exc_info=True,
                    )

                # Store in cache
                if rank is not None:
                    self._get_cache_for_collection(opensea_slug, rank_provider)[
                        str(token_id)
                    ] = rank

            if rank:
                token_with_rarity.rarities.append(
                    RarityData(provider=rank_provider, rank=rank)
                )

        if cache_external_ranks:
            self.write_cache_to_file(opensea_slug, rank_provider)

        return tokens_with_rarity

    # Cache methods
    def _load_cache_from_file(
        self,
        slug: str,
        rank_provider: RankProvider,
        force_reload: bool = False,
    ) -> bool:
        # Short-circuit if cache is already loaded, unless we want to force a reload
        if not force_reload and self._is_cache_loaded(slug, rank_provider):
            return False

        cache_filename = self.cache_filename(rank_provider=rank_provider, slug=slug)
        try:
            with open(cache_filename) as jsonfile:
                external_rank_data = json.load(jsonfile)
            logger.debug(
                f"Successfully loaded cached external ranks from: {cache_filename}: "
                f"Found {len(external_rank_data)} token ranks"
            )
        except FileNotFoundError:
            logger.warning(f"Cache file does not exist: {cache_filename}.")
            return False
        except Exception:
            logger.exception(
                f"Could not parse cache file: {cache_filename}.", exc_info=True
            )
            return False

        self._set_cache(
            slug=slug, rank_provider=rank_provider, rank_data=external_rank_data
        )
        return True

    def write_cache_to_file(self, slug: str, rank_provider: RankProvider):
        cache_data = self._get_cache_for_collection(
            slug=slug, rank_provider=rank_provider
        )
        cache_filename = self.cache_filename(rank_provider=rank_provider, slug=slug)
        logger.debug(
            f"Writing external rank data ({rank_provider}) to cache for: {slug} "
            f"to file: {cache_filename}. Contains {len(cache_data)} token ranks."
        )
        with open(cache_filename, "w+") as jsonfile:
            json.dump(cache_data, jsonfile, indent=4)

    def _set_cache(
        self, slug: str, rank_provider: RankProvider, rank_data: dict[str, int]
    ) -> None:
        self._get_cache(rank_provider)[slug] = rank_data

    def _get_cache(self, rank_provider: RankProvider) -> dict[str, dict[str, int]]:
        if rank_provider == RankProvider.TRAITS_SNIPER:
            return self._trait_sniper_cache
        if rank_provider == RankProvider.RARITY_SNIFFER:
            return self._rarity_sniffer_cache
        if rank_provider == RankProvider.RARITY_SNIPER:
            return self._rarity_sniper_cache
        raise Exception(f"Unknown external rank provider: {rank_provider}")

    def _get_cache_for_collection(
        self, slug: str, rank_provider: RankProvider
    ) -> dict[str, int]:
        return self._get_cache(rank_provider)[slug]

    def _get_cached_rank(
        self, slug: str, rank_provider: RankProvider, token_id: int
    ) -> int | None:
        return self._get_cache_for_collection(slug, rank_provider).get(
            str(token_id), None
        )

    def _is_cache_loaded(self, slug: str, rank_provider: RankProvider):
        return (
            len(self._get_cache_for_collection(rank_provider=rank_provider, slug=slug))
            > 0
        )
