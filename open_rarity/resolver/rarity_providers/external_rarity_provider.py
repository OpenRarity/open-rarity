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

from .rarity_sniffer import RaritySnifferResolver
from .rarity_sniper import RaritySniperResolver
from .trait_sniper import TraitSniperResolver

logger = logging.getLogger("open_rarity_logger")


class ExternalRarityProvider:
    # Cached file will have format:
    # "cached_{provider_name}_ranks-{collection slug}.json"
    # The data must be a dictionary of <token id as int> to <rank as int>
    CACHE_FILENAME_FORMAT: str = "cached_data/cached_%s_ranks-%s.json"

    # Dictionary of slug -> {token_id (str) -> rank (int)}
    _trait_sniper_external_rank_cache: dict[str, dict[str, int]] = defaultdict(dict)
    _rarity_sniffer_external_rank_cache: dict[str, dict[str, int]] = defaultdict(dict)
    _rarity_sniper_external_rank_cache: dict[str, dict[str, int]] = defaultdict(dict)

    def cache_filename(self, rank_provider: RankProvider, slug: str) -> str:
        rank_name = rank_provider.name.lower()
        return self.CACHE_FILENAME_FORMAT % (rank_name, slug)

    def write_cache_to_file(self, slug: str, rank_provider: RankProvider):
        cache_data = self._get_provider_rank_cache(
            slug=slug, rank_provider=rank_provider
        )
        cache_filename = self.cache_filename(rank_provider=rank_provider, slug=slug)
        logger.debug(
            f"Writing external rank data ({rank_provider}) to cache for: {slug} "
            f"to file: {cache_filename}. Contains {len(cache_data)} token ranks."
        )
        with open(cache_filename, "w+") as jsonfile:
            json.dump(cache_data, jsonfile, indent=4)

    def _get_provider_rank_cache(
        self, slug: str, rank_provider: RankProvider
    ) -> dict[str, int]:
        if rank_provider == RankProvider.TRAITS_SNIPER:
            return self._trait_sniper_external_rank_cache[slug]
        if rank_provider == RankProvider.RARITY_SNIFFER:
            return self._rarity_sniffer_external_rank_cache[slug]
        if rank_provider == RankProvider.RARITY_SNIPER:
            return self._rarity_sniper_external_rank_cache[slug]
        raise Exception(f"Unknown external rank provider: {rank_provider}")

    def _get_cached_rank(
        self, slug: str, rank_provider: RankProvider, token_id: int
    ) -> int | None:
        return self._get_provider_rank_cache(slug, rank_provider).get(
            str(token_id), None
        )

    def _is_cache_loaded(self, slug: str, rank_provider: RankProvider):
        return (
            len(self._get_provider_rank_cache(rank_provider=rank_provider, slug=slug))
            > 0
        )

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
        if rank_provider == RankProvider.TRAITS_SNIPER:
            self._trait_sniper_external_rank_cache[slug] = external_rank_data
        elif rank_provider == RankProvider.RARITY_SNIFFER:
            self._rarity_sniffer_external_rank_cache[slug] = external_rank_data
        elif rank_provider == RankProvider.RARITY_SNIPER:
            self._rarity_sniper_external_rank_cache[slug] = external_rank_data
        else:
            raise Exception(f"Unknown external rank provider: {rank_provider}")

        return True

    def _add_trait_sniper_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        cache_external_ranks: bool = True,
    ) -> list[TokenWithRarityData]:
        """Modifies `tokens_with_rarity` by adding trait sniper rank
        If trait sniper API is not reachable, rank for that token will not be added.

        Parameters
        ----------
        collection_with_metadata : CollectionWithMetadata
        tokens : list[TokenWithRarityData]
            batch of tokens to resolve with existing rarity data
            This may not be all the tokens in collection.tokens

        Returns
        -------
        list[TokenWithRarityData]: returns input `tokens_with_rarity`
            augmented with trait_sniper rank added to rarities field
        """
        logger.debug("Resolving trait sniper rarity")
        rank_provider = RankProvider.TRAITS_SNIPER

        # We're currently using opensea slug to calculate trait sniper slug
        slug = collection_with_metadata.opensea_slug
        if cache_external_ranks:
            # Try to load cache with a local cache file
            self._load_cache_from_file(slug=slug, rank_provider=rank_provider)

        # If we didn't want to load cache or cache is empty, pull data from API
        # in bulk and store it in cache
        if not self._is_cache_loaded(slug=slug, rank_provider=rank_provider):
            contract_addresses = collection_with_metadata.contract_addresses
            assert (len(contract_addresses)) == 1
            try:
                trait_sniper_rank_data = TraitSniperResolver.get_all_ranks(
                    contract_address=contract_addresses[0]
                )
                logger.debug(
                    f"Resolved trait sniper rarity for {slug=} {contract_addresses[0]}"
                )
            except Exception:
                logger.exception(
                    "Failed to resolve Traits Sniper ranking data",
                    exc_info=True,
                )
                return tokens_with_rarity
            if not trait_sniper_rank_data:
                logger.warning(f"[TraitSniper] Did not get any data for {slug}")
                return tokens_with_rarity

            # Load cache with fetched data
            rank_cache = self._get_provider_rank_cache(
                slug=slug, rank_provider=rank_provider
            )
            for ts_rank_data in trait_sniper_rank_data:
                token_id = str(ts_rank_data["token_id"])
                rank_cache[token_id] = int(ts_rank_data["rarity_rank"])

            self.write_cache_to_file(slug, rank_provider)

        for token_with_rarity in tokens_with_rarity:
            token = token_with_rarity.token
            token_identifer = token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id
            rank = None

            rank = self._get_cached_rank(
                slug=slug, rank_provider=rank_provider, token_id=token_id
            )

            if rank:
                token_with_rarity.rarities.append(
                    RarityData(provider=RankProvider.TRAITS_SNIPER, rank=rank)
                )

        return tokens_with_rarity

    def _add_rarity_sniffer_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        cache_external_ranks: bool = True,
    ) -> list[TokenWithRarityData]:
        """Modifies `tokens_with_rarity` by adding rarity sniffer rank data
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
        rank_provider = RankProvider.RARITY_SNIFFER
        slug = collection_with_metadata.opensea_slug
        logger.debug(f"Resolving rarity sniffer for {slug}")

        contract_addresses = collection_with_metadata.contract_addresses
        if len(contract_addresses) != 1:
            raise ValueError(
                "We cannot calculate rarity sniffer score for collections "
                f"that do not map to a single contract address: {contract_addresses=}"
            )

        contract_address = contract_addresses[0]
        if cache_external_ranks:
            self._load_cache_from_file(slug=slug, rank_provider=rank_provider)

        # If there was no cache data available, make API request to fetch data
        if not self._is_cache_loaded(slug, rank_provider):
            try:
                token_ids_to_ranks = RaritySnifferResolver.get_ranks(
                    contract_address=contract_address
                )

                self._rarity_sniffer_external_rank_cache[slug] = token_ids_to_ranks
                num_tokens = len(token_ids_to_ranks)
                logger.debug(
                    f"Fetched {num_tokens} token ranks from rarity sniffer API"
                )
                self.write_cache_to_file(slug, rank_provider)
            except Exception:
                logger.exception("Failed to resolve token_ids Rarity Sniffer")
                raise

        for token_with_rarity in tokens_with_rarity:
            token_identifer = token_with_rarity.token.token_identifier
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id: int = token_identifer.token_id

            # Get rank either from cache or from API memoization dict
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

                # Write to cache
                self._get_provider_rank_cache(opensea_slug, rank_provider)[
                    str(token_id)
                ] = rank

            if rank:
                token_with_rarity.rarities.append(
                    RarityData(provider=rank_provider, rank=rank)
                )

        return tokens_with_rarity

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
            If set to true, will use local cache file instead of fetching rank data

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
                if rank_provider == RankProvider.RARITY_SNIFFER:
                    self._add_rarity_sniffer_rarity_data(
                        collection_with_metadata=collection_with_metadata,
                        tokens_with_rarity=tokens_with_rarity,
                        cache_external_ranks=cache_external_ranks,
                    )
                if rank_provider == RankProvider.TRAITS_SNIPER:
                    self._add_trait_sniper_rarity_data(
                        collection_with_metadata=collection_with_metadata,
                        tokens_with_rarity=tokens_with_rarity,
                        cache_external_ranks=cache_external_ranks,
                    )
                if rank_provider == RankProvider.RARITY_SNIPER:
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
