import pytest

from open_rarity.resolver.rarity_providers.trait_sniper import TraitSniperProvider


class TestTraitSniperProvider:
    BORED_APE_COLLECTION_ADDRESS = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long due to rate limits to have as part of CI/CD "
        "but should be run whenver someone changes resolvers",
    )
    def test_get_all_ranks(self):
        token_ranks = TraitSniperProvider.get_all_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS
        )
        assert len(token_ranks) == 10000

    def test_get_ranks(self):
        token_ranks = TraitSniperProvider.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=1
        )
        assert len(token_ranks) == 200
        token_ranks = TraitSniperProvider.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=50
        )
        assert len(token_ranks) == 200

    def test_get_ranks_no_more_data(self):
        token_ranks = TraitSniperProvider.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=51
        )
        assert len(token_ranks) == 0

    def test_get_ranks_no_contract(self):
        token_ranks = TraitSniperProvider.get_ranks(contract_address="0x123", page=1)
        assert len(token_ranks) == 0

    def test_get_rank(self):
        rank = TraitSniperProvider.get_rank(
            collection_slug="boredapeyachtclub",
            token_id=1000,
        )
        assert rank
