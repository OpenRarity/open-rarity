import logging
import os
import sys
from itertools import chain
from typing import Any, Iterable, cast

import httpx
from satchel.iterable import chunk
from tenacity import before_sleep, retry, stop, wait
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential

from openrarity.token import RawToken, TokenId
from openrarity.token.types import MetadataAttribute
from openrarity.utils.aio import ratelimited_gather

from .types import TokenAsset

logging.basicConfig(format=f"%(message)s",stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)


class OpenseaApiRateLimitError(Exception):
    pass


class OpenseaApi:
    """
    This is a class to work with `OpenseaApi`. It handles fetching and transforming of token data.

    Attributes
    ----------
    USER_AGENT :
        User Agent.
    COLLECTION_URL : str
        Opensea collection data url. This will be used to fetch specific collection_data.
    ASSETS_URL : str
        Opensea assets data url. This will be used to fetch token_data by token_ids.
    API_KEY : str
        Opensea api key. Optionally, we can pass our own api_key using environment variable.
        Example : OPENSEA_API_KEY = <API_KEY>
    RATE_LIMIT : int
        Api request Concurrency limit. we can set this limit value using environment variable.
        Example : OPENSEA_API_RPS = <RATE_LIMIT>
    HEADERS : dict
        Api headers.
    """
    USER_AGENT = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
    }
    # https://docs.opensea.io/reference/retrieving-a-single-collection
    COLLECTION_URL = "https://api.opensea.io/api/v1/collection/{slug}"
    ASSETS_URL = "https://api.opensea.io/api/v1/assets"
    API_KEY = os.environ.get("OPENSEA_API_KEY", "")
    RATE_LIMIT = int(os.environ.get("OPENSEA_API_RPS", 4))
    HEADERS = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY,
    }
    # https://docs.opensea.io/docs/metadata-standards

    @classmethod
    def fetch_opensea_collection_data(cls, slug: str) -> list[TokenAsset]:
        """Fetches collection data from Opensea's GET collection endpoint for
        the given slug.

        Parameters
        ----------
        slug: str
            Opensea collection slug. Example : boredapeyachtclub.

        Returns
        -------
        list[TokenAsset]
            Collection data of a given slug.

        Raises
        ------
        HTTPError
            If api request fails, it returns `HTTPError` object with Traceback error and status code.
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
        """Transform the Opensea Asset api response into the format for OpenRarity's
        `TokenCollection` class.

        Parameters
        ----------
        responses : Iterable[TokenAsset]
            An iterable of Opensea api get response.

        Returns
        -------
        dict[TokenId, RawToken]
            Returns OpenRarity input format data.
        """
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
        """For the given token ids, It fetches asset data using Opensea's GET assets endpoint.

        Parameters
        ----------
        slug: str
            Opensea collection slug. Example : boredapeyachtclub.
        token_ids: list[int]
            List of token ids to fetch the token_data.
        limit: int, optional
            How many tokens to fetch at once. Defaults to 30, with a max of 30.

        Returns
        -------
        dict[TokenId, RawToken]
            Returns OpenRarity input format data.

        Raises
        ------
            HTTPError
                If api request fails, it returns `HTTPError` object with Traceback error and status code.
        """
        # Max 30 limit enforced on API
        assert limit <= 30
        async with httpx.AsyncClient(headers=cls.HEADERS, timeout=None) as client:
            responses: list[httpx.Response] = await ratelimited_gather(
                cls.RATE_LIMIT,
                coros=[
                    _send_request(  # type: ignore
                        client,
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


@retry(
    wait=wait_exponential(1),
    stop=stop_after_attempt(7),
    before_sleep=before_sleep.before_sleep_log(logger, logging.WARN),
)
async def _send_request(client: "httpx.AsyncClient", url: str, params: dict[str, Any]):
    """
    Deferred function to fetch params from a url and handle errors. Note that it returns a specific error for rate limits and non-200 responses.

    Parameters
    ----------
    client: "httpx.AsyncClient"
        HTTPX async client to fetch token data.
    url: str
        URL to submit GET request with provided query args against.
    params: dict[str, Any]
        The required query arguments to fetch token data.
        Query arguments include
            - token_ids : list[str]
            - collection_silg : str
            - offset : str
            - limit : int

    Returns
    -------
    httpx.Response
        Returns httpx response from GET call.

    Raises
    ------
    HTTPError | OpenseaApiRateLimitError
        If the api request rate exceedes the limit, it raises OpenseaApiRateLimitError exception. And for others, it returns a `HTTPError` object with Traceback error and status code.
    """
    response = await client.get(url, params=params)
    if response.status_code == 429:
        raise OpenseaApiRateLimitError("Rate Limit Exceeded")
    elif response.status_code != 200:
        response.raise_for_status()

    return response
