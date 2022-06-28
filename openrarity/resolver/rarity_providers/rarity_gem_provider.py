import logging
from openrarity.models.collection import Collection
from openrarity.models.token import Rank, RankProvider, Token
from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By

GEM_XYZ_URL = "https://www.gem.xyz/asset/{contract}/{id}"

logger = logging.getLogger("testset_resolver")


class GemRarityResolver:
    def resolve_rank_element(
        self,
        driver: ChromeDriverManager,
        css_class_name: str,
        rank_provider: RankProvider,
    ) -> Rank:
        """Utility function that resolves HTML element with selenium driver

        Parameters
        ----------
        driver : ChromeDriverManager
            chrome selenium driver
        css_class_name : str
            css class nam of the element

        Returns
        -------
        Rank
            rank of the specific provider
        """
        elem = driver.find_element(
            By.CLASS_NAME,
            css_class_name,
        )
        rank = int(elem.text.strip("#"))
        logger.debug("Resolved rank {rank}".format(rank=(rank_provider, rank)))
        return (rank_provider, rank)

    def resovle_rank(
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
        for token in tokens:
            logger.debug(
                "Resolving token {token} from collection {coll}".format(
                    token=token.token_id, coll=collection.slug
                )
            )
            url = GEM_XYZ_URL.format(
                contract=collection.contract_address, id=token.token_id
            )
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install())
            )
            driver.implicitly_wait(10)

            logger.debug("Gem resolution url " + url)
            driver.get(url)
            token_ranks = []

            # fmt: off
            try:
                rarity_sniper = self.resolve_rank_element(
                    driver,
                    "flex.pr-2.whitespace-nowrap.items-center",
                    RankProvider.RARITY_SNIPER,
                )
                token_ranks.append(rarity_sniper)
            except Exception:
                logger.exception("Rarity Sniper resolution failed")

            try:
                trait_sniper = self.resolve_rank_element(
                    driver,
                    "flex.pr-2.border-2.rounded-md.ml-2.h-6.pl-1.font-bold.text-xs.flex.items-center.justify-center.whitespace-nowrap.items-center", # noqa: E501,E261
                    RankProvider.TRAITS_SNIPER
                )
                token_ranks.append(trait_sniper)
            except Exception:
                logger.exception("Trait Sniper resolution failed")

            try:
                gem_ranking = self.resolve_rank_element(
                    driver,
                    "border-2.border-white.rounded-md.text-white.h-6.px-2.font-bold.text-xs.flex.items-center.justify-center", # noqa: E501,E261
                    RankProvider.GEM
                )
                token_ranks.append(gem_ranking)
            except Exception:
                logger.exception("Gem resolution failed")
            token.ranks = token_ranks
            logger.debug(
                """Computed ranks {ranks}""".format(ranks=token_ranks)
            )
            # fmt: on

            driver.close()

        return tokens
