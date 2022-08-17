from open_rarity.resolver.models.token_with_rarity_data import RankProvider


class TestTestsetResolver:
    bayc_token_ids_to_ranks = {
        # Rare token
        1: {
            RankProvider.RARITY_SNIFFER: 1,  # todo
            RankProvider.TRAITS_SNIPER: 2,  # todo
            RankProvider.RARITY_SNIPER: 3,  # todo
            RankProvider.OR_ARITHMETIC: 4,  # todo
            RankProvider.OR_INFORMATION_CONTENT: 5,  # todo
        },
        # Middle token
        5000: {
            RankProvider.RARITY_SNIFFER: 1,  # todo
            RankProvider.TRAITS_SNIPER: 2,  # todo
            RankProvider.RARITY_SNIPER: 3,  # todo
            RankProvider.OR_ARITHMETIC: 4,  # todo
            RankProvider.OR_INFORMATION_CONTENT: 5,  # todo
        },
        # Common token
        9489: {
            RankProvider.RARITY_SNIFFER: 1,  # todo
            RankProvider.TRAITS_SNIPER: 2,  # todo
            RankProvider.RARITY_SNIPER: 3,  # todo
            RankProvider.OR_ARITHMETIC: 4,  # todo
            RankProvider.OR_INFORMATION_CONTENT: 5,  # todo
        },
    }
