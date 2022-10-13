from open_rarity.resolver.rarity_providers.rarity_sniper import RaritySniperProvider


class TestRaritySniperProvider:
    BORED_APE_SLUG = "bored-ape-yacht-club"

    def test_get_rank(self):
        rank = RaritySniperProvider.get_rank(
            collection_slug=self.BORED_APE_SLUG,
            token_id=1020,
        )
        # We don't check ranks since they can change ranks
        assert rank

    def test_get_rank_no_contract(self):
        rank = RaritySniperProvider.get_rank(
            collection_slug="non_existent_slug", token_id=1
        )
        assert rank is None
