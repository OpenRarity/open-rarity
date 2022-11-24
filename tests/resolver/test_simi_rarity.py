import pytest

from open_rarity.resolver.rarity_providers.rank_resolver import RankResolver
from open_rarity.resolver.rarity_providers.simi_rarity import SimiRarityResolver

class TestSimiRarityResolver:
    AZUKI_COLLECTION_ADDRESS = "0xed5af388653567af2f388e6224dc7c4b3241c544"

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long due to rate limits to have as part of CI/CD "
        "but should be run whenver someone changes resolvers.",
    )
    def test_get_all_ranks(self):
        token_ranks = SimiRarityResolver.get_all_ranks(
            contract_address=self.AZUKI_COLLECTION_ADDRESS
        )
        assert len(token_ranks) == 200

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This requires API key",
    )
    def test_get_ranks_first_page(self):
        token_ranks = SimiRarityResolver.get_ranks(
            contract_address=self.AZUKI_COLLECTION_ADDRESS, page=1
        )
        assert len(token_ranks) == 200

    # @pytest.mark.skipif(
    #     "not config.getoption('--run-resolvers')",
    #     reason="This requires API key",
    # )
    # def test_get_ranks_max_page(self):
    #     token_ranks = TraitSniperResolver.get_ranks(
    #         contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=50
    #     )
    #     assert len(token_ranks) == 200

    # def test_get_ranks_no_more_data(self):
    #     token_ranks = TraitSniperResolver.get_ranks(
    #         contract_address=self.BORED_APE_COLLECTION_ADDRESS, page=51
    #     )
    #     assert len(token_ranks) == 0

    def test_get_ranks_no_slug(self):
        token_ranks = SimiRarityResolver.get_ranks(slug="cdrg", page=1)
        assert len(token_ranks) == 0

    def test_get_rank(self):
        rank = SimiRarityResolver.get_rank(
            collection_slug="azuki",
            token_id=2286,
        )
        assert rank

    def test_rank_resolver_parent(self):
        assert isinstance(SimiRarityResolver, RankResolver)
