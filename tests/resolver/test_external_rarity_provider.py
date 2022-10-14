import pytest

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.resolver.models.collection_with_metadata import CollectionWithMetadata
from open_rarity.resolver.models.token_with_rarity_data import (
    RankProvider,
    TokenWithRarityData,
)
from open_rarity.resolver.rarity_providers.external_rarity_provider import (
    ExternalRarityProvider,
)


class TestExternalRarityProvider:
    bayc_address = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"
    bayc_collection = CollectionWithMetadata(
        collection=Collection(tokens=[]),
        contract_addresses=[bayc_address],
        token_total_supply=10_000,
        opensea_slug="boredapeyachtclub",
    )
    bayc_token_1 = Token.from_erc721(
        contract_address=bayc_address,
        token_id=1,
        metadata_dict={
            "mouth": "grin",
            "background": "orange",
            "eyes": "blue beams",
            "fur": "robot",
            "clothes": "vietnam jacket",
        },
    )

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long due to rate limits to have as part of CI/CD "
        "but should be run whenver someone changes resolvers. Also needs "
        "TRAIT_SNIPER_API_KEY key",
    )
    def test_fetch_and_update_ranks_all_providers(self):
        provider = ExternalRarityProvider()
        tokens_with_rarity = [TokenWithRarityData(token=self.bayc_token_1, rarities=[])]
        provider.fetch_and_update_ranks(
            collection_with_metadata=self.bayc_collection,
            tokens_with_rarity=tokens_with_rarity,
            cache_external_ranks=False,
        )
        rarities = tokens_with_rarity[0].rarities
        assert len(rarities) == 3

    def test_fetch_and_update_ranks_rarity_sniffer_sniper(self):
        provider = ExternalRarityProvider()
        tokens_with_rarity = [TokenWithRarityData(token=self.bayc_token_1, rarities=[])]
        provider.fetch_and_update_ranks(
            collection_with_metadata=self.bayc_collection,
            tokens_with_rarity=tokens_with_rarity,
            cache_external_ranks=False,
            rank_providers=[RankProvider.RARITY_SNIFFER, RankProvider.RARITY_SNIPER],
        )
        rarities = tokens_with_rarity[0].rarities
        assert len(rarities) == 2
        for rarity in rarities:
            assert rarity.provider in [
                RankProvider.RARITY_SNIFFER,
                RankProvider.RARITY_SNIPER,
            ]
            assert rarity.rank
