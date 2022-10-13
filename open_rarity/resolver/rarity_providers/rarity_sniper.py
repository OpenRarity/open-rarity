import logging

import requests

from .rank_resolver import RankResolver

logger = logging.getLogger("open_rarity_logger")
RARITY_SNIPER_API_URL = (
    "https://api.raritysniper.com/public/collection/{slug}/id/{token_id}"
)
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}


class RaritySniperResolver(RankResolver):
    @staticmethod
    def get_all_ranks(slug: str) -> dict[str, int]:
        raise NotImplementedError

    @staticmethod
    def get_slug(opensea_slug: str) -> str:
        # custom fixes to normalize slug name
        # used in rarity sniper
        slug = opensea_slug.replace("-nft", "")
        slug = slug.replace("-official", "")
        slug = slug.replace("beanzofficial", "beanz")
        slug = slug.replace("boredapeyachtclub", "bored-ape-yacht-club")
        slug = slug.replace("clonex", "clone-x")
        slug = slug.replace("invisiblefriends", "invisible-friends")
        slug = slug.replace("proof-", "")
        slug = slug.replace("pudgypenguins", "pudgy-penguins")
        slug = slug.replace("wtf", "")

        return slug

    @staticmethod
    def get_rank(collection_slug: str, token_id: int) -> int | None:
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
