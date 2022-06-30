import logging

import requests
from openrarity.models.collection import Collection
from openrarity.models.token import Rank, RankProvider, Token


TRAIT_SNIPER_URL = "https://api.traitsniper.com/api/projects/{slug}/nfts"
RARITY_SNIFFER_API_URL = "https://raritysniffer.com/api/index.php"

logger = logging.getLogger("testset_resolver")


class ExternalRarityProvider:

    rarity_sniffer_state: dict[str, dict[int, Rank]] = {}

    def __resolver_trait_sniper(
        self, collection: Collection, tokens: list[Token]
    ) -> list[Token]:

        logger.debug("Resolving trait sniper rarity")
        try:
            querystring = {
                "trait_norm": "true",
                "trait_count": "true",
                "token_id": ",".join([str(t.token_id) for t in tokens]),
            }

            response = requests.request(
                "GET",
                TRAIT_SNIPER_URL.format(slug=collection.slug),
                params=querystring,
            )

            if response.status_code != 200:
                logger.debug(
                    "Failed to resolve token_ids Trait Sniper. Reason {resp}".format(
                        resp=response
                    )
                )
                return tokens

            scores: dict[int, Rank] = {
                int(nft["token_id"]): (
                    RankProvider.TRAITS_SNIPER,
                    nft["rarity_rank"],
                )
                for nft in response.json()["nfts"]
            }

            logger.debug(
                "Resolved rarity scores {scores}".format(scores=scores)
            )

            for token in tokens:
                token.ranks.append(scores[token.token_id])
        except Exception:
            logger.exception("Failed to resolve token_ids Traits Sniper")

        return tokens

    def __rarity_sniffer_nft_score(
        self, collection: Collection
    ) -> dict[int, Rank]:
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
                "GET", RARITY_SNIFFER_API_URL, params=querystring
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

        logger.debug("Resolving rarity sniffer")
        try:
            for token in tokens:

                token.ranks.append(
                    self.__rarity_sniffer_nft_score(collection=collection)[
                        token.token_id
                    ]
                )
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

        for token in tokens:
            logger.debug(
                "Resolving token {token} from collection {coll}".format(
                    token=token.token_id, coll=collection.slug
                )
            )

            augmented_tokens = self.__resolver_rarity_sniffer(
                collection=collection, tokens=tokens
            )

            augmented_tokens_final.extend(
                self.__resolver_trait_sniper(
                    collection=collection, tokens=augmented_tokens
                )
            )

            logger.debug(
                """Computed ranks {ranks}""".format(
                    ranks=augmented_tokens_final
                )
            )

        return augmented_tokens_final
