import logging

import requests
from openrarity.models.collection import Collection
from openrarity.models.token_identifier import EVMContractTokenIdentifier
from openrarity.resolver.models.token_with_rarity_data import RankProvider, RarityData, TokenWithRarityData

TRAIT_SNIPER_URL = "https://api.traitsniper.com/api/projects/{slug}/nfts"
RARITY_SNIFFER_API_URL = "https://raritysniffer.com/api/index.php"
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}
logger = logging.getLogger("open_rarity_logger")


def fetch_trait_sniper_rank_for_evm_token(collection_slug: str, token_id: int) -> int | None:
    """Sends a GET request to Trait Sniper API to fetch ranking
    data for a given EVM token. Trait Sniper uses opensea slug as a param.

    Args:
        collection_slug (str): collection slug of collection you're attempting to fetch
            This must be the slug on trait sniper's slug system.
        token_id (int): the token number

    Returns:
        Rarity rank for given token ID if request was successful, otherwise None.
    """
    # TODO [vicky]: In future, we can add retry mechanisms if needed

    querystring = {
        "trait_norm": "true",
        "trait_count": "true",
        "token_id": token_id,
    }

    if not collection_slug:
        raise Exception(f"Unable to fetch trait sniper rank as slug is invalid. Slug={collection_slug}")

    url = TRAIT_SNIPER_URL.format(slug=collection_slug)
    response = requests.request("GET", url, params=querystring, headers=USER_AGENT)
    if response.status_code == 200:
        return int(response.json()["nfts"][0]["rarity_rank"])
    else:
        logger.debug(
            f"[TraitSniper] Failed to resolve TraitSniper rank for {collection_slug} {token_id}. "
            f"Received {response.status_code} for {url}: {response.reason}. {response.json()}"
        )
        return None


def get_trait_sniper_slug(opensea_slug: str):
    # Trait Sniper's slug is slightly different than opensea's slug.
    # For many cases, ew can simply get rid of the "-nft" from the slug to transform
    # to one that is accepted by TraitSniper, and it's relatively accurate.
    # TODO [dan]: to change this
    return opensea_slug.replace("-nft", "")


def fetch_rarity_sniffer_rank_for_collection(contract_address: str) -> dict[int, RarityData]:
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
            f"[RaritySniffer] Failed to resolve Rarity Sniffer ranks for {contract_address}. "
            f"Received: {response.status_code}: {response.reason} {response.json()}"
        )
        raise Exception("RaritySniffer fetching failed for {contract_address}")

    tokens_to_rarity_data: dict[int, RarityData] = {
        int(nft["id"]): (RankProvider.RARITY_SNIFFER, nft["positionId"], None) for nft in response.json()["data"]
    }

    return tokens_to_rarity_data


class ExternalRarityProvider:

    # Cache of rarity sniffer ranking data for given contracts
    # since rarity sniffer API does a bulk reques for an entire collection
    # Key = Contract Address
    # Value = Token ID -> RarityData
    rarity_sniffer_state: dict[str, dict[int, RarityData]] = {}

    def _add_trait_sniper_rarity_data(
        self, collection: Collection, tokens_with_rarity: list[TokenWithRarityData]
    ) -> list[TokenWithRarityData]:
        """Modifies `tokens_with_rarity` by adding trait sniper rank
        If trait sniper API is not reachable, rank for that token will not be added.

        Parameters
        ----------
        collection : Collection
            collection. We currently only support Collection's that have an identifer type of
            OpenseaCollectionIdentifier since we use the opensea slug to help determine
            the url/collection to fetch.
        tokens : list[TokenWithRarityData]
            batch of tokens to resolve with existing rarity data
            This may not be all the tokens in collection.tokens

        Returns
        -------
        list[TokenWithRarityData]: returns input `tokens_with_rarity`
            augmented `tokens_with_rarity` with trait_sniper rank added to rarities field
        """
        logger.debug("Resolving trait sniper rarity")

        # We currently only support EVM collections on trait sniper
        if collection.token_identifier_types != [EVMContractTokenIdentifier.identifier_type]:
            error_message = f"Cannot fetch rarity sniper rankings for non EVM collection {collection.name}"
            logger.exception(error_message)
            raise Exception(error_message)

        # We're currently using opensea slug to calculate trait sniper slug
        slug = collection.opensea_slug
        assert slug
        slug = get_trait_sniper_slug(opensea_slug=slug)

        for token_with_rarity in tokens_with_rarity:
            token = token_with_rarity.token
            token_identifer = token.token_identifier
            # Needed for type-checking
            assert isinstance(token_identifer, EVMContractTokenIdentifier)
            token_id = token_identifer.token_id

            try:
                logger.debug(f"Resolving trait sniper rarity for collection {slug} token_id {token_id}")

                rank = fetch_trait_sniper_rank_for_evm_token(collection_slug=slug, token_id=token_id)

                if rank is None:
                    continue

                token_rarity_data: RarityData = (RankProvider.TRAITS_SNIPER, rank, None)
                logger.debug(f"Resolved trait sniper rarity for collection {slug} token_id {token_id}: {rank}")
                token_with_rarity.rarities.append(token_rarity_data)

            except Exception:
                logger.exception("Failed to resolve token_ids Traits Sniper")

        return tokens_with_rarity

    def _add_rarity_sniffer_rarity_data(
        self, collection: Collection, tokens_with_rarity: list[TokenWithRarityData]
    ) -> list[TokenWithRarityData]:
        """Modifies `tokens_with_rarity` by adding rarity sniffer rank data
        Currently only works for EVM collections

        Parameters
        ----------
        collection : Collection
            collection
        tokens_with_rarity : list[TokenWithRarityData]
            list of tokens with rarity to augment

        Returns
        -------
        list[TokenWithRarityData]
            list of augmeneted tokens
        """

        logger.debug("Resolving rarity sniffer")
        contract_addresses = collection.contract_addresses
        if len(contract_addresses) != 1:
            raise Exception(
                "We cannot calculate rarity sniffer score for collections "
                f"that do not map to a single contract address: {contract_addresses=}"
            )

        contract_address = contract_addresses[0]
        token_rarity_data = {}
        try:
            # Memoize since caller typically calls this function with the same collection
            # but different batches of tokens
            if contract_address not in self.rarity_sniffer_state:
                self.rarity_sniffer_state[contract_address] = fetch_rarity_sniffer_rank_for_collection(
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
            logger.debug(f"Fetched Rarirty Sniffer rarity score for [{collection}]{token_identifer}: {rarity_data}")

        return tokens_with_rarity

    def fetch_and_update_ranks(
        self,
        collection: Collection,
        tokens_with_rarity: list[TokenWithRarityData],
        rank_providers: list[RankProvider] = [RankProvider.TRAITS_SNIPER, RankProvider.RARITY_SNIFFER],
    ) -> list[TokenWithRarityData]:
        """Fetches ranks from available providers gem, rarity sniper and/or trait sniper
        and adds them to the rarities field in `tokens_with_rarity`

        Parameters
        ----------
        collection : Collection
            collection
        tokens_with_rarity: list[TokenWithRaritydata]
            List of tokens with rarity data.
            Will modify the objects.rarities field and add the fetched ranking data directly to object.

        Returns
        -------
        list[tokens_with_rarity]
            tokens with fetched external rarity data
        """
        logger.debug(len(tokens_with_rarity))

        for rank_provider in rank_providers:
            if rank_provider == RankProvider.RARITY_SNIFFER:
                self._add_rarity_sniffer_rarity_data(collection=collection, tokens_with_rarity=tokens_with_rarity)
            if rank_provider == RankProvider.TRAITS_SNIPER:
                self._add_trait_sniper_rarity_data(collection=collection, tokens_with_rarity=tokens_with_rarity)

        return tokens_with_rarity
