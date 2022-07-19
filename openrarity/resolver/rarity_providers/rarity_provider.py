import logging

import requests
from openrarity.models.collection import Collection
from openrarity.models.token import Rank, RankProvider, Token


TRAIT_SNIPER_URL = "https://api.traitsniper.com/api/projects/{slug}/nfts"
RARITY_SNIFFER_API_URL = "https://raritysniffer.com/api/index.php"
USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
}
logger = logging.getLogger("open_rarity_logger")


class ExternalRarityProvider:

    rarity_sniffer_state: dict[str, dict[int, Rank]] = {}

    def __resolver_trait_sniper(
        self, collection: Collection, tokens: list[Token]
    ) -> list[Token]:
        """Resolves the rarity from the list
            of tokens

        Parameters
        ----------
        collection : Collection
            collection
        tokens : list[Token]
            batch of tokens to resolve

        Returns
        -------
        list[Token]
            augmented tokens with trait_sniper rank
        """
        logger.debug("Resolving trait sniper rarity")

        for token in tokens:
            try:
                logger.debug(
                    "Resolving trait sniper rarity for token_id {id}".format(
                        id=token.token_id
                    )
                )

                querystring = {
                    "trait_norm": "true",
                    "trait_count": "true",
                    "token_id": token.token_id,
                }

                slug = collection.slug.replace("-nft", "")

                url = TRAIT_SNIPER_URL.format(slug=slug)

                logger.debug("{url}".format(url=url))

                response = requests.request(
                    "GET", url, params=querystring, headers=USER_AGENT
                )

                if response.status_code != 200:
                    logger.debug(
                        "Failed to resolve token_ids Trait Sniper.\
                        Status {code} Reason {resp}".format(
                            resp=response.json(), code=response.reason
                        )
                    )
                    return tokens

                asset = response.json()["nfts"][0]

                token_rank: Rank = (
                    RankProvider.TRAITS_SNIPER,
                    asset["rarity_rank"],
                )

                logger.debug(
                    "Resolved rarity scores {rank}".format(rank=token_rank)
                )

                token.ranks.append(token_rank)

            except Exception:
                logger.exception("Failed to resolve token_ids Traits Sniper")

        return tokens

    def __rarity_sniffer_nft_score(
        self, collection: Collection
    ) -> dict[int, Rank]:
        """Pre-loads all available tokens and ranks
            to the local dict for the fast processing.
            Internal private method.

        Parameters
        ----------
        collection : Collection
            collection

        Returns
        -------
        dict[int, Rank]
            dictionary with token_id as key and rank as value

        Raises
        ------
        Exception
            If call to the rarity sniffer failed the
            method throws exception
        """

        if collection.contract_address not in self.rarity_sniffer_state:
            querystring = {
                "query": "fetch",
                "collection": collection.contract_address,
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
                    "Failed to resolve token_ids Rarity Sniffer. Reason {resp}".format(
                        resp=response
                    )
                )
                raise Exception("exception during the sniffer resolution")

            scores: dict[int, Rank] = {
                int(nft["id"]): (
                    RankProvider.RARITY_SNIFFER,
                    nft["positionId"],
                )
                for nft in response.json()["data"]
            }

            self.rarity_sniffer_state[collection.contract_address] = scores

        return self.rarity_sniffer_state[collection.contract_address]

    def __resolver_rarity_sniffer(
        self, collection: Collection, tokens: list[Token]
    ) -> list[Token]:
        """Resolves rarity from RaritySniffer API

        Parameters
        ----------
        collection : Collection
            collection
        tokens : list[Token]
            list of tokens to augment

        Returns
        -------
        list[Token]
            list of augmeneted tokens
        """

        logger.debug("Resolving rarity sniffer")
        try:
            for token in tokens:

                collection_ranks = self.__rarity_sniffer_nft_score(
                    collection=collection
                )

                rank = collection_ranks[int(token.token_id)]

                token.ranks.append(rank)

                logger.debug("Resolved rarity scores {rank}".format(rank=rank))

        except Exception:
            logger.exception("Failed to resolve token_ids Rarity Sniffer")

        return tokens

    def resolve_rank(
        self,
        collection: Collection,
        tokens: list[Token],
    ) -> list[Token]:
        """Resolves ranks from avaialbe providers gem, rarity sniper and trait sniper

        Parameters
        ----------
        collection : Collection
            collection
        tokens : list[Token]
            list of tokens to augment

        Returns
        -------
        list[Token]
            augmented tokens with ranks
        """
        augmented_tokens_final = []

        logger.debug(len(tokens))

        # resolve ranks from Rarity Sniffer
        rarity_sniffer_tokens = self.__resolver_rarity_sniffer(
            collection=collection, tokens=tokens
        )

        # resolve ranks from Rarity Sniper
        augmented_tokens_final.extend(
            self.__resolver_trait_sniper(
                collection=collection, tokens=rarity_sniffer_tokens
            )
        )

        return augmented_tokens_final
