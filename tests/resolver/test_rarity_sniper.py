import pytest

from open_rarity.resolver.rarity_providers.rank_resolver import RankResolver
from open_rarity.resolver.rarity_providers.rarity_sniper import RaritySniperResolver


class TestRaritySniperResolver:
    BORED_APE_SLUG = "bored-ape-yacht-club"

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="Requires the live RaritySniper API",
    )
    def test_get_rank(self):
        rank = RaritySniperResolver.get_rank(
            collection_slug=self.BORED_APE_SLUG,
            token_id=1020,
        )
        # We don't check ranks since they can change ranks
        assert rank

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="Requires the live RaritySniper API",
    )
    def test_get_rank_no_contract(self):
        rank = RaritySniperResolver.get_rank(
            collection_slug="non_existent_slug", token_id=1
        )
        assert rank is None

    def test_rank_resolver_parent(self):
        assert isinstance(RaritySniperResolver, RankResolver)
