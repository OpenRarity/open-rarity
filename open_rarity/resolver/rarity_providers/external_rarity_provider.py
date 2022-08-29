import logging

import requests
from open_rarity.resolver.models.collection_with_metadata import (
    CollectionWithMetadata,
)
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.resolver.models.token_with_rarity_data import (
    RankProvider,
    RarityData,
    TokenWithRarityData,
    EXTERNAL_RANK_PROVIDERS,
)

TRAIT_SNIPER_URL = "https://api.traitsniper.com/api/projects/{slug}/nfts"
RARITY_SNIFFER_API_URL = "https://raritysniffer.com/api/index.php"
RARITY_SNIPER_API_URL = (
    "https://api.raritysniper.com/public/collection/{slug}/id/{token_id}"
)
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}
logger = logging.getLogger("open_rarity_logger")


def fetch_trait_sniper_rank_for_evm_token(
    collection_slug: str, token_id: int
) -> int | None:
    """Sends a GET request to Trait Sniper API to fetch ranking
    data for a given EVM token. Trait Sniper uses opensea slug as a param.

    Parameters
    ----------
    collection_slug : str
        collection slug of collection you're attempting to fetch. This must be
        the slug on trait sniper's slug system.
    token_id : int
        the token number.

    Returns
    -------
    int | None
        Rarity rank for given token ID if request was successful, otherwise None.

    Raises
    ------
    ValueError
        If slug is invalid.
    """
    # TODO [vicky]: In future, we can add retry mechanisms if needed

    querystring = {
        "trait_norm": "true",
        "trait_count": "true",
        "token_id": token_id,
    }

    if not collection_slug:
        msg = f"Failed to fetch traitsniper rank as slug is invalid. {collection_slug=}"
        logger.exception(msg)
        raise ValueError(msg)

    url = TRAIT_SNIPER_URL.format(slug=collection_slug)
    response = requests.request(
        "GET", url, params=querystring, headers=USER_AGENT
    )
    if response.status_code == 200:
        return int(response.json()["nfts"][0]["rarity_rank"])
    else:
        logger.debug(
            "[TraitSniper] Failed to resolve TraitSniper rank for "
            f"{collection_slug} {token_id}. Received {response.status_code} "
            f"for {url}: {response.reason}. {response.json()}"
        )
        return None


def fetch_rarity_sniffer_rank_for_collection(
    contract_address: str,
) -> dict[int, RarityData]:
    """Fetches all available tokens and ranks
       for a given collection from rarity sniffer.
       Only usable for EVM tokens and collections for a single
       contract address.

    Parameters
    ----------
    contract_address : The contract address of the collection

    Returns
    -------
    dict[int, RarityData]: Dictionary of token ID # to the RarityData

    Raises
    ------
    Exception
        If call to the rarity sniffer failed the method throws exception
    """

    querystring = {
        "query": "fetch",
        "collection": contract_address,
        "taskId": "any",
        "norm": "true",
        "partial": "false",
        "traitCount": "true",
    }

    response = requests.request(
        "GET",
        RARITY_SNIFFER_API_URL,
        params=querystring,
        headers=USER_AGENT,
    )

    if response.status_code != 200:
        logger.debug(
            "[RaritySniffer] Failed to resolve Rarity Sniffer ranks for "
            f"{contract_address}. Received: {response.status_code}: "
            f"{response.reason} {response.json()}"
        )
        response.raise_for_status()

    tokens_to_rarity_data: dict[int, RarityData] = {
        int(nft["id"]): RarityData(
            provider=RankProvider.RARITY_SNIFFER, rank=nft["positionId"]
        )
        for nft in response.json()["data"]
    }

    return tokens_to_rarity_data


def get_rarity_sniper_slug(opensea_slug: str) -> str:
    # custom fixes to normalize slug name
    # used in rarity sniper
    slug = opensea_slug.replace("-nft", "")
    slug = slug.replace("-official", "")
    slug = slug.replace("proof-", "")
    slug = slug.replace("wtf", "")
    slug = slug.replace("invisiblefriends", "invisible-friends")
    slug = slug.replace("boredapeyachtclub", "bored-ape-yacht-club")
    return slug


def fetch_rarity_sniper_rank_for_evm_token(
    collection_slug: str, token_id: int
) -> int | None:
    url = RARITY_SNIPER_API_URL.format(slug=collection_slug, token_id=token_id)
    logger.debug("{url}".format(url=url))
    response = requests.request("GET", url, headers=USER_AGENT)
    if response.status_code == 200:
        return response.json()["rank"]
    else:
        logger.debug(
            f"[RaritySniper] Failed to resolve Rarity Sniper rank for "
            f"{collection_slug} {token_id}. Received {response.status_code} for "
            f"{url}: {response.reason}. {response.json()}"
        )
        return None


class ExternalRarityProvider:

    # Cache of rarity sniffer ranking data for given contracts
    # since rarity sniffer API does a bulk reques for an entire collection
    # Key = Contract Address
    # Value = Token ID -> RarityData
    rarity_sniffer_state: dict[str, dict[int, RarityData]] = {}

    def _add_trait_sniper_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
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

        # We're currently using opensea slug to calculate trait sniper slug
        slug = collection_with_metadata.opensea_slug

        for token_with_rarity in tokens_with_rarity:
            token = token_with_rarity.token
            token_identifer = token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id

            try:
                logger.debug(
                    f"Resolving trait sniper rarity for {slug=} {token_id=}"
                )

                rank = fetch_trait_sniper_rank_for_evm_token(
                    collection_slug=slug, token_id=token_id
                )

                if rank is None:
                    continue

                token_rarity_data = RarityData(
                    provider=RankProvider.TRAITS_SNIPER, rank=rank
                )
                logger.debug(
                    f"Resolved trait sniper rarity for {slug=} {token_id=}: {rank}"
                )
                token_with_rarity.rarities.append(token_rarity_data)

            except Exception:
                logger.exception("Failed to resolve token_ids Traits Sniper")

        return tokens_with_rarity

    def _add_rarity_sniffer_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
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

        logger.debug("Resolving rarity sniffer")
        contract_addresses = collection_with_metadata.contract_addresses
        if len(contract_addresses) != 1:
            raise ValueError(
                "We cannot calculate rarity sniffer score for collections "
                f"that do not map to a single contract address: {contract_addresses=}"
            )

        contract_address = contract_addresses[0]
        token_rarity_data = {}
        try:
            # Memoize since caller typically calls this function with the same
            # collection but different batches of tokens
            if contract_address not in self.rarity_sniffer_state:
                self.rarity_sniffer_state[
                    contract_address
                ] = fetch_rarity_sniffer_rank_for_collection(
                    contract_address=contract_address
                )
        except Exception:
            logger.exception("Failed to resolve token_ids Rarity Sniffer")
            raise

        token_rarity_data = self.rarity_sniffer_state[contract_address]
        for token_with_rarity in tokens_with_rarity:
            token_identifer = token_with_rarity.token.token_identifier
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            rarity_data = token_rarity_data[int(token_identifer.token_id)]

            token_with_rarity.rarities.append(rarity_data)
            slug = collection_with_metadata.opensea_slug
            logger.debug(
                f"Fetched Rarirty Sniffer rarity score for {slug=} "
                f"{token_identifer}: {rarity_data}"
            )

        return tokens_with_rarity

    def _add_rarity_sniper_rarity_data(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
    ) -> list[TokenWithRarityData]:
        # We're currently using opensea slug to calculate trait sniper slug
        opensea_slug = collection_with_metadata.opensea_slug
        slug = get_rarity_sniper_slug(opensea_slug=opensea_slug)

        for token_with_rarity in tokens_with_rarity:
            token = token_with_rarity.token
            token_identifer = token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id

            try:
                logger.debug(
                    f"Resolving rarity sniper rarity for {slug=} {token_id=}"
                )

                rank = fetch_rarity_sniper_rank_for_evm_token(
                    collection_slug=slug, token_id=token_id
                )

                if rank is None:
                    continue

                token_rarity_data = RarityData(
                    provider=RankProvider.RARITY_SNIPER, rank=rank
                )
                logger.debug(
                    f"Resolved rarity sniper rarity for {slug=} {token_id=}: {rank}"
                )
                token_with_rarity.rarities.append(token_rarity_data)

            except Exception:
                logger.exception("Failed to resolve token_ids Rarity Sniper")

        return tokens_with_rarity

    def fetch_and_update_ranks(
        self,
        collection_with_metadata: CollectionWithMetadata,
        tokens_with_rarity: list[TokenWithRarityData],
        rank_providers: list[RankProvider] = EXTERNAL_RANK_PROVIDERS,
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

        Returns
        -------
        list[tokens_with_rarity]
            tokens with fetched external rarity data
        """
        logger.debug(len(tokens_with_rarity))

        for rank_provider in rank_providers:
            if rank_provider == RankProvider.RARITY_SNIFFER:
                self._add_rarity_sniffer_rarity_data(
                    collection_with_metadata=collection_with_metadata,
                    tokens_with_rarity=tokens_with_rarity,
                )
            if rank_provider == RankProvider.TRAITS_SNIPER:
                self._add_trait_sniper_rarity_data(
                    collection_with_metadata=collection_with_metadata,
                    tokens_with_rarity=tokens_with_rarity,
                )
            if rank_provider == RankProvider.RARITY_SNIPER:
                self._add_rarity_sniper_rarity_data(
                    collection_with_metadata=collection_with_metadata,
                    tokens_with_rarity=tokens_with_rarity,
                )

        return tokens_with_rarity
