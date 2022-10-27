import logging
import os
import time

import requests

from .rank_resolver import RankResolver

logger = logging.getLogger("open_rarity_logger")
# For fetching rank fetches for an entire contract
TRAIT_SNIPER_RANKS_URL = (
    "https://api.traitsniper.com/v1/collections/{contract_address}/ranks"
)
# For single rank fetches
TRAIT_SNIPER_NFTS_URL = "https://api.traitsniper.com/api/projects/{slug}/nfts"

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}
API_KEY = os.environ.get("TRAIT_SNIPER_API_KEY") or ""


class TraitSniperResolver(RankResolver):
    @staticmethod
    def get_all_ranks(contract_address: str) -> dict[str, int]:
        """Get all ranks for a contract address

        Returns
        -------
        dict[str, int]
            A dictionary of token_id to ranks
        """
        rank_data_page = TraitSniperResolver.get_ranks(contract_address, page=1)
        all_rank_data = rank_data_page
        page = 2

        while rank_data_page:
            rank_data_page = TraitSniperResolver.get_ranks(contract_address, page=page)
            all_rank_data.extend(rank_data_page)
            page += 1
            # Due to rate limits we need to slow things down a bit...
            # Free tier is 5 request per second
            time.sleep(12)

        return {
            str(rank_data["token_id"]): int(rank_data["rarity_rank"])
            for rank_data in all_rank_data
            if rank_data["rarity_rank"]
        }

    @staticmethod
    def get_ranks(contract_address: str, page: int, limit: int = 200) -> list[dict]:
        """
        Parameters
        ----------
        contract_address: str
            The contract address of collection you're fetching ranks for
        limit: int
            The number of ranks to fetch. Defaults to 200, and maxes at 200
            due to API limitations.

        Returns
        -------
            List of rarity rank data from trait sniper API with the following
            data structure for each item in the list:
            {
                "rarity_rank": int,
                "rarity_score": float
                "token_id": str
            }

        Requires
        --------
            API KEY

        Raises
        ------
            ValueError if contract address is None
        """
        if not contract_address:
            msg = f"Failed to fetch traitsniper. {contract_address=} is invalid."
            logger.exception(msg)
            raise ValueError(msg)

        url = TRAIT_SNIPER_RANKS_URL.format(contract_address=contract_address)
        headers = {
            **USER_AGENT,
            **{"X-TS-API-KEY": API_KEY},
        }
        query_params = {
            "limit": max(limit, 200),
            "page": page,
        }
        response = requests.request("GET", url, headers=headers, params=query_params)
        if response.status_code == 200:
            return response.json()["ranks"]
        else:
            if (
                "Collection could not be found on TraitSniper"
                in response.json()["message"]
            ):
                logger.warning(
                    f"[TraitSniper] Collection not found: {contract_address}"
                )
            else:
                logger.debug(
                    "[TraitSniper] Failed to resolve TraitSniper rank for "
                    f"{contract_address}. Received {response.status_code} "
                    f"for {url}: {response.reason}. {response.json()}"
                )
            return []

    @staticmethod
    def get_rank(collection_slug: str, token_id: int) -> int | None:
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

        querystring: dict[str, str | int] = {
            "trait_norm": "true",
            "trait_count": "true",
            "token_id": token_id,
        }

        if not collection_slug:
            msg = "Cannot fetch traitsniper rank as slug is None."
            logger.exception(msg)
            raise ValueError(msg)

        url = TRAIT_SNIPER_NFTS_URL.format(slug=collection_slug)
        response = requests.request("GET", url, params=querystring, headers=USER_AGENT)
        if response.status_code == 200:
            return int(response.json()["nfts"][0]["rarity_rank"])
        else:
            logger.debug(
                "[TraitSniper] Failed to resolve TraitSniper rank for "
                f"{collection_slug} {token_id}. Received {response.status_code} "
                f"for {url}: {response.reason}. {response.json()}"
            )
            return None
