import logging
import os
import time

import requests

from .rank_resolver import RankResolver

logger = logging.getLogger("open_rarity_logger")
# For fetching ranks for the entire collection
SIMIRARITY_RANKS_URL = (
    "http://localhost:3000/similarity/collections/ranking/{slug}"
)
# For single token rank
SIMIRARITY_TOKEN_RANK_URL = "http://localhost:3000/similarity/collections/ranking/{slug}/{id}"

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}
API_KEY = os.environ.get("TRAIT_SNIPER_API_KEY") or ""


class SimiRarityResolver(RankResolver):
    @staticmethod
    def get_all_ranks(slug: str) -> dict[str, int]:
        """Get all ranks for a contract address

        Returns
        -------
        dict[str, int]
            A dictionary of token_id to ranks
        """
        rank_data_page = SimiRarityResolver.get_ranks(contract_address, page=1)
        all_rank_data = rank_data_page
        page = 2

        while rank_data_page:
            rank_data_page = SimiRarityResolver.get_ranks(contract_address, page=page)
            all_rank_data.extend(rank_data_page)
            page += 1
            # To avoid any possible rate limits we need to slow things down a bit...
            time.sleep(10)

        return {
            str(rank_data["id"]): int(rank_data["rank"])
            for rank_data in all_rank_data
            if rank_data["rank"]
        }

    @staticmethod
    def get_ranks(slug: str, page: int, limit: int = 200) -> list[dict]:
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
                "similairy": float,
                "id": int,
                "percentile": int,
                "rank": int,
                "image": str
            }

        Raises
        ------
            ValueError if contract address is None
        """
        if not slug:
            msg = f"Failed to fetch traitsniper. {slug=} is invalid."
            logger.exception(msg)
            raise ValueError(msg)

        url = SIMIRARITY_RANKS_URL.format(slug=slug)
        # headers = {
        #     **USER_AGENT,
        #     **{"X-TS-API-KEY": API_KEY},
        # }
        # query_params = {
        #     "limit": max(limit, 200),
        #     "page": page,
        # }
        response = requests.request("GET", url)
        if response.status_code == 200:
            return response.json()
        else:
            if (
                "Internal Server Error"
                in response.json()["message"]
            ):
                logger.warning(
                    f"[SimiRarity] Collection not found: {slug}"
                )
            else:
                logger.debug(
                    "[SimiRarity] Failed to resolve SimiRarity rank for "
                    f"collection {slug}. Received {response.status_code} "
                    f"for {url}: {response.json()}"
                )
            return []

    @staticmethod
    def get_rank(collection_slug: str, token_id: int) -> int | None:
        """Sends a GET request to SimiRarity API to fetch ranking ifno
        for a given token. SimiRarity uses opensea slug as a param.

        Parameters
        ----------
        collection_slug : str
            collection slug of collection you're attempting to fetch. This must be
            the slug on SimiRarity's slug system.
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

        # querystring: dict[str, str | int] = {
        #     "trait_norm": "true",
        #     "trait_count": "true",
        #     "token_id": token_id,
        # }

        if not collection_slug:
            msg = "Cannot fetch token rank info for an empty slug."
            logger.exception(msg)
            raise ValueError(msg)

        url = SIMIRARITY_TOKEN_RANK_URL.format(slug=collection_slug, id=token_id)
        logger.debug(" sent url {url}")
        response = requests.request("GET", url)
        logger.debug(" res url {response}")
        if response.status_code == 200:
            return int(response.json()["rank"])
        else:
            logger.debug(
                "[SimiRarity] Failed to resolve rank for "
                f"{collection_slug} {token_id}. Received {response.status_code} "
                f"for {url}: {response.json()}"
            )
            return None
