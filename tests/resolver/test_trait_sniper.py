import pytest

from open_rarity.resolver.rarity_providers.rank_resolver import RankResolver
from open_rarity.resolver.rarity_providers.trait_sniper import TraitSniperResolver

# NOTE: API_KEY is needed for these tests (TRAIT_SNIPER_API_KEY must be set)


class TestTraitSniperResolver:
    BORED_APE_COLLECTION_ADDRESS = "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d"

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long due to rate limits to have as part of CI/CD "
        "but should be run whenver someone changes resolvers. Also needs API key",
    )
    def test_get_all_ranks(self):
        token_ranks = TraitSniperResolver.get_all_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS
        )
        assert len(token_ranks) == 10000

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_ranks_first_page(self):
        token_ranks = TraitSniperResolver.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=1
        )
        assert len(token_ranks) == 200

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_ranks_max_page(self):
        token_ranks = TraitSniperResolver.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=50
        )
        assert len(token_ranks) == 200

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_ranks_no_more_data(self):
        token_ranks = TraitSniperResolver.get_ranks(
            contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=51
        )
        assert len(token_ranks) == 0

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_ranks_no_contract(self):
        token_ranks = TraitSniperResolver.get_ranks(contract_address="0x123", page=1)
        assert len(token_ranks) == 0

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_rank(self):
        rank = TraitSniperResolver.get_rank(
            collection_slug="boredapeyachtclub",
            token_id=1000,
        )
        assert rank

    def test_rank_resolver_parent(self):
        assert isinstance(TraitSniperResolver, RankResolver)
