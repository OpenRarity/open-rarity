import logging

import requests

from .rank_resolver import RankResolver

logger = logging.getLogger("open_rarity_logger")
RARITY_SNIFFER_API_URL = "https://raritysniffer.com/api/index.php"
USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
    )
}


class RaritySnifferResolver(RankResolver):
    @staticmethod
    def get_all_ranks(contract_address: str) -> dict[str, int]:
        """Fetches all available tokens and ranks
        for a given collection from rarity sniffer.
        Only usable for EVM tokens and collections for a single
        contract address.

        Parameters
        ----------
        contract_address : The contract address of the collection

        Returns
        -------
        dict[int, int]: Dictionary of token ID # to the rank. Empty if no data.

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

        data = response.json().get("data", None)
        if "Not found" in response.json().get("error", "") or not data:
            logger.exception(
                f"[RaritySniffer] No data for {contract_address}. "
                f"Json response: {response.json()}",
                exc_info=True,
            )
            return {}
        try:
            token_ids_to_ranks = {
                str(nft["id"]): int(nft["positionId"]) for nft in data
            }
        except Exception:
            logger.exception(
                f"[RaritySniffer] Data could not be parsed for {contract_address}. "
                f"Json response: {response.json()}",
                exc_info=True,
            )
            return {}

        return token_ids_to_ranks
