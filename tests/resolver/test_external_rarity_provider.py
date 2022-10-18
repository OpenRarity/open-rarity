import pytest

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.resolver.models.collection_with_metadata import CollectionWithMetadata
from open_rarity.resolver.models.token_with_rarity_data import (
    EXTERNAL_RANK_PROVIDERS,
    RankProvider,
    TokenWithRarityData,
)
from open_rarity.resolver.rarity_providers.external_rarity_provider import (
    ExternalRarityProvider,
)
from open_rarity.resolver.rarity_providers.rarity_sniffer import RaritySnifferResolver
from open_rarity.resolver.rarity_providers.rarity_sniper import RaritySniperResolver
from open_rarity.resolver.rarity_providers.trait_sniper import TraitSniperResolver


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
        reason="Dependent on external API and takes too long due to rate limits"
        "Should only be used to verify external API changes and needs "
        "TRAIT_SNIPER_API_KEY key",
    )
    def test_fetch_and_update_ranks_real_api_calls(self):
        provider = ExternalRarityProvider()
        tokens_with_rarity = [TokenWithRarityData(token=self.bayc_token_1, rarities=[])]
        provider.fetch_and_update_ranks(
            collection_with_metadata=self.bayc_collection,
            tokens_with_rarity=tokens_with_rarity,
            cache_external_ranks=False,
        )
        rarities = tokens_with_rarity[0].rarities
        assert len(rarities) == 3

    def test_fetch_and_update_ranks_mocked_api(self, mocker):
        provider = ExternalRarityProvider()
        tokens_with_rarity = [TokenWithRarityData(token=self.bayc_token_1, rarities=[])]

        rarity_sniffer_rank = 3256
        rarity_sniper_rank = 3250
        trait_sniper_rank = 3000
        mocker.patch.object(
            RaritySnifferResolver,
            "get_all_ranks",
            return_value={"1": rarity_sniffer_rank},
        )
        mocker.patch.object(
            TraitSniperResolver, "get_all_ranks", return_value={"1": trait_sniper_rank}
        )
        mocker.patch.object(
            RaritySniperResolver, "get_rank", return_value=rarity_sniper_rank
        )

        provider.fetch_and_update_ranks(
            collection_with_metadata=self.bayc_collection,
            tokens_with_rarity=tokens_with_rarity,
            cache_external_ranks=False,
        )
        rarities = tokens_with_rarity[0].rarities
        assert len(rarities) == 3
        for rarity in rarities:
            assert rarity.provider in EXTERNAL_RANK_PROVIDERS
            if rarity.provider == RankProvider.RARITY_SNIFFER:
                assert rarity.rank == rarity_sniffer_rank
            elif rarity.provider == RankProvider.RARITY_SNIPER:
                assert rarity.rank == rarity_sniper_rank
            elif rarity.provider == RankProvider.TRAITS_SNIPER:
                assert rarity.rank == trait_sniper_rank
            else:
                raise Exception("Unexpected provider")
