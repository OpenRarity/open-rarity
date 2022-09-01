import pytest

from open_rarity.resolver.models.token_with_rarity_data import RankProvider
from open_rarity.resolver.testset_resolver import resolve_collection_data


class TestTestsetResolver:
    # Note: Official ranking is rarity tools (linked by site)
    bayc_token_ids_to_ranks = {
        # Rare token, official rank=1
        7495: {
            # https://app.traitsniper.com/boredapeyachtclub?view=7495
            RankProvider.TRAITS_SNIPER: "1",
            # https://raritysniffer.com/viewcollection/boredapeyachtclub?nft=7495
            RankProvider.RARITY_SNIFFER: "3",
            # https://raritysniper.com/bored-ape-yacht-club/7495
            RankProvider.RARITY_SNIPER: "1",
            RankProvider.OR_ARITHMETIC: "1",
            RankProvider.OR_INFORMATION_CONTENT: "1",
        },
        # Middle token, official rank=3503
        509: {
            # https://app.traitsniper.com/boredapeyachtclub?view=509
            RankProvider.TRAITS_SNIPER: "3370",
            # https://raritysniffer.com/viewcollection/boredapeyachtclub?nft=509
            RankProvider.RARITY_SNIFFER: "3257",
            # https://raritysniper.com/bored-ape-yacht-club/509
            RankProvider.RARITY_SNIPER: "3402",
            RankProvider.OR_ARITHMETIC: "2988",
            RankProvider.OR_INFORMATION_CONTENT: "3748",
        },
        # Common token, official rank=7623
        8002: {
            # https://app.traitsniper.com/boredapeyachtclub?view=8002
            RankProvider.TRAITS_SNIPER: "6810",
            # https://raritysniffer.com/viewcollection/boredapeyachtclub?nft=8002
            RankProvider.RARITY_SNIFFER: "7709",
            # https://raritysniper.com/bored-ape-yacht-club/8002
            RankProvider.RARITY_SNIPER: "6924",
            RankProvider.OR_ARITHMETIC: "6003",
            RankProvider.OR_INFORMATION_CONTENT: "6818",
        },
    }

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long to have as part of CI/CD but should be "
        "run whenver someone changes resolver",
    )
    def test_resolve_collection_data(self):
        # Have the resolver pull in BAYC rarity rankings from various sources
        # Just do a check to ensure the ranks from different providers are
        # as expected
        resolve_collection_data(
            resolve_remote_rarity=True,
            package_path="tests",
            filename="resolver/sample_files/bayc.json",
            # max_tokens_to_calculate=100,
        )
        # Read the file and verify columns values are as expected for the given tokens
        output_filename = "testset_boredapeyachtclub.csv"
        import csv

        rows = 0
        with open(output_filename) as csvfile:
            resolver_output_reader = csv.reader(csvfile)
            for idx, row in enumerate(resolver_output_reader):
                rows += 1
                print(", ".join(row))
                if idx == 0:
                    assert row[0] == "slug"
                    assert row[1] == "token_id"
                    assert row[2] == "traits_sniper"
                    assert row[3] == "rarity_sniffer"
                    assert row[4] == "rarity_sniper"
                    assert row[5] == "arithmetic"
                    assert row[6] == "geometric"
                    assert row[7] == "harmonic"
                    assert row[8] == "sum"
                    assert row[9] == "information_content"
                else:
                    token_id = int(row[1])
                    if token_id in self.bayc_token_ids_to_ranks:
                        assert row[0] == "boredapeyachtclub"
                        expected_ranks = self.bayc_token_ids_to_ranks[token_id]
                        assert (
                            row[2]
                            == expected_ranks[RankProvider.TRAITS_SNIPER]
                        )
                        assert (
                            row[3]
                            == expected_ranks[RankProvider.RARITY_SNIFFER]
                        )
                        assert (
                            row[4]
                            == expected_ranks[RankProvider.RARITY_SNIPER]
                        )
                        assert (
                            row[5]
                            == expected_ranks[RankProvider.OR_ARITHMETIC]
                        )
                        assert (
                            row[9]
                            == expected_ranks[
                                RankProvider.OR_INFORMATION_CONTENT
                            ]
                        )

        assert rows == 10_001
