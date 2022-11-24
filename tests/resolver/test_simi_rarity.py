import pytest

from open_rarity.resolver.rarity_providers.rank_resolver import RankResolver
from open_rarity.resolver.rarity_providers.simi_rarity import SimiRarityResolver

class TestSimiRarityResolver:
    AZUKI_COLLECTION_SLUG = "azuki"

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long due to rate limits to have as part of CI/CD "
        "but should be run whenver someone changes resolvers.",
    )
    def test_get_all_ranks(self):
        simi_rarity_resolver = SimiRarityResolver()
        token_ranks = simi_rarity_resolver.get_all_ranks(
            collection_slug=self.AZUKI_COLLECTION_SLUG
        )
        assert len(token_ranks) == 200

    # @pytest.mark.skipif(
    #     "not config.getoption('--run-resolvers')",
    #     reason="This requires API key",
    # )
    def test_get_ranks_first_page(self):
        simi_rarity_resolver = SimiRarityResolver()
        token_ranks = simi_rarity_resolver.get_ranks(
            collection_slug=self.AZUKI_COLLECTION_SLUG, offset=0
        )
        assert len(token_ranks) == 50

    def test_slug_supported(self):
        simi_rarity_resolver = SimiRarityResolver()
        slug_exists = simi_rarity_resolver.is_supported(collection_slug=self.AZUKI_COLLECTION_SLUG)
        assert slug_exists

    def test_slug_not_supported(self):
        simi_rarity_resolver = SimiRarityResolver()
        slug_exists = simi_rarity_resolver.is_supported(collection_slug="bayc")
        assert not slug_exists

    def test_get_ranks_no_slug(self):
        simi_rarity_resolver = SimiRarityResolver()
        with pytest.raises(ValueError, match=r"Collection collection_slug='cdrg' is not supported."):
            simi_rarity_resolver.get_ranks(collection_slug="cdrg", offset=0)

    def test_get_rank(self):
        simi_rarity_resolver = SimiRarityResolver()
        rank = simi_rarity_resolver.get_rank(
            collection_slug=self.AZUKI_COLLECTION_SLUG,
            token_id=2286,
        )
        assert rank

    def test_rank_resolver_parent(self):
        assert isinstance(SimiRarityResolver, RankResolver)
