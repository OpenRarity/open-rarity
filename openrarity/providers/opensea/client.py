import logging
import os
from itertools import chain
from typing import Iterable, cast

import httpx
from satchel.iterable import chunk

from openrarity.token import RawToken, TokenId
from openrarity.token.types import MetadataAttribute
from openrarity.utils.aio import semaphore_gather

from .types import TokenAsset

logger = logging.getLogger(__name__)


class OpenseaApi:
    USER_AGENT = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
    }
    # https://docs.opensea.io/reference/retrieving-a-single-collection
    COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
    ASSETS_URL = "https://api.opensea.io/api/v1/assets"
    API_KEY = os.environ.get("OPENSEA_API_KEY", "")
    RATE_LIMIT_SEMAPHORE = 5 if API_KEY else 2
    HEADERS = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY,
    }
    # https://docs.opensea.io/docs/metadata-standards

    @staticmethod
    def transform(data: list[TokenAsset]) -> dict[TokenId, RawToken]:
        """Transform the Opensea Asset api response into the format for OpenRarity's
        `TokenCollection` class.

        Parameters
        ----------
        data : list[TokenAsset]
            Api response data.

        Returns
        -------
        dict[TokenId, RawToken]
            OpenRarity input format
        """
        return {  # type: ignore
            str(t["token_identifier"]["token_id"]): {  # type: ignore
                "attributes": [
                    {"name": name, "value": value}
                    for name, value in t["metadata_dict"].items()  # type: ignore
                ]
            }
            for t in data
        }

    @classmethod
    def fetch_opensea_collection_data(cls, slug: str) -> list[TokenAsset]:
        """Fetches collection data from Opensea's GET collection endpoint for
        the given slug.

        Raises:
            Exception: If API request fails
        """
        response = httpx.get(cls.COLLECTION_URL.format(slug=slug))

        if response.status_code != 200:
            logger.debug(
                f"[Opensea] Failed to resolve collection {slug}."
                f"Received {response.status_code}: {response.reason_phrase}. {response.json()}"
            )

            response.raise_for_status()

        return response.json()["collection"]

    @classmethod
    def transform_assets_response(
        cls, responses: Iterable[TokenAsset]
    ) -> dict[TokenId, RawToken]:
        return {  # type: ignore
            asset["token_id"]: {
                "attributes": [
                    cast(
                        MetadataAttribute,
                        {
                            k: attr.setdefault(k, None)  # type: ignore
                            for k in ("trait_type", "value", "display_type")
                        },
                    )
                    for attr in asset["traits"]
                ]
            }
            for asset in responses
        }

    @classmethod
    async def fetch_opensea_assets_data(
        cls, slug: str, token_ids: list[str], limit: int = 30
    ) -> dict[TokenId, RawToken]:
        """Fetches asset data from Opensea's GET assets endpoint for the given token ids

        Parameters
        ----------
        slug: str
            Opensea collection slug
        token_ids: list[int]
            the token id
        limit: int, optional
            How many to fetch at once. Defaults to 30, with a max of 30, by default 30.

        Returns
        -------
        list[dict]
            list of asset data dictionaries, e.g. the response in "assets" field,
            sorted by token_id asc

        Raises
        ------
            Exception: If api request fails


        """

        # Max 30 limit enforced on API
        assert limit <= 30
        async with httpx.AsyncClient(headers=cls.HEADERS) as client:
            responses: list[httpx.Response] = await semaphore_gather(
                2,
                coros=[
                    client.get(  # type: ignore
                        cls.ASSETS_URL,
                        params={
                            "token_ids": tids,
                            "collection_slug": slug,
                            "offset": "0",
                            "limit": limit,
                        },
                    )
                    for tids in chunk(token_ids, limit)
                ],
            )

            # TODO: Better error handling
            for r in responses:
                if r.status_code != 200:
                    r.raise_for_status()
                    logger.warn(f"[Opensea] Failed to resolve assets for {slug}.")

            return cls.transform_assets_response(
                chain(*[r.json()["assets"] for r in responses])
            )
