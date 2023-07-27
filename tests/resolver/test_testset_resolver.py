import csv

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
            RankProvider.OR_INFORMATION_CONTENT: "1",
        },
        # Middle token, official rank=3503
        509: {
            # https://app.traitsniper.com/boredapeyachtclub?view=509
            RankProvider.TRAITS_SNIPER: "2730",
            # https://raritysniffer.com/viewcollection/boredapeyachtclub?nft=509
            RankProvider.RARITY_SNIFFER: "3257",
            # https://raritysniper.com/bored-ape-yacht-club/509
            RankProvider.RARITY_SNIPER: "3402",
            RankProvider.OR_INFORMATION_CONTENT: "4091",
        },
        # Common token, official rank=7623
        8002: {
            # https://app.traitsniper.com/boredapeyachtclub?view=8002
            RankProvider.TRAITS_SNIPER: "6271",
            # https://raritysniffer.com/viewcollection/boredapeyachtclub?nft=8002
            RankProvider.RARITY_SNIFFER: "7709",
            # https://raritysniper.com/bored-ape-yacht-club/8002
            RankProvider.RARITY_SNIPER: "6924",
            RankProvider.OR_INFORMATION_CONTENT: "7347",
        },
    }
    ic_bayc_token_ids_to_ranks = {
        "2100": 10,
        "5757": 11,
        "7754": 12,
        "5020": 3101,
        "1730": 3102,
        "6784": 7344,
        "5949": 7345,
        "2103": 5414,
        "980": 5415,
        "5525": 9999,
        "5777": 10000,
    }

    EXPECTED_COLUMNS = [
        "slug",
        "token_id",
        "traits_sniper",
        "rarity_sniffer",
        "rarity_sniper",
        "arithmetic",
        "geometric",
        "harmonic",
        "sum",
        "information_content",
    ]

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long to have as part of CI/CD but should be "
        "run whenver someone changes resolver",
    )
    def test_resolve_collection_data_two_providers(self):
        # Have the resolver pull in BAYC rarity rankings from various sources
        # Just do a check to ensure the ranks from different providers are
        # as expected
        resolve_collection_data(
            resolve_remote_rarity=True,
            package_path="tests",
            # We exclude trait sniper due to API key requirements
            external_rank_providers=[
                RankProvider.RARITY_SNIFFER,
                RankProvider.RARITY_SNIPER,
            ],
            filename="resolver/sample_files/bayc.json",
        )
        # Read the file and verify columns values are as expected for the given tokens
        output_filename = "testset_boredapeyachtclub.csv"

        rows = 0
        with open(output_filename) as csvfile:
            resolver_output_reader = csv.reader(csvfile)
            for idx, row in enumerate(resolver_output_reader):
                rows += 1
                if idx == 0:
                    assert row[0:10] == self.EXPECTED_COLUMNS
                else:
                    token_id = int(row[1])
                    if token_id in self.bayc_token_ids_to_ranks:
                        assert row[0] == "boredapeyachtclub"
                        expected_ranks = self.bayc_token_ids_to_ranks[token_id]
                        assert row[3] == expected_ranks[RankProvider.RARITY_SNIFFER]
                        assert row[4] == expected_ranks[RankProvider.RARITY_SNIPER]
                        assert row[5] == expected_ranks[RankProvider.OR_ARITHMETIC]
                        assert (
                            row[9]
                            == expected_ranks[RankProvider.OR_INFORMATION_CONTENT]
                        )

        assert rows == 10_001

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests runs too long to have as part of CI/CD but should be "
        "run whenever someone changes resolver and requires TRAIT_SNIPER_API_KEY",
    )
    # Warning: Trait Sniper ranks are not stable, so this test may fail.
    # If it does, just update the expected values to be what's on the site.
    def test_resolve_collection_data_traits_sniper(self):
        # Have the resolver pull in BAYC rarity rankings from various sources
        # Just do a check to ensure the ranks from different providers are
        # as expected
        resolve_collection_data(
            resolve_remote_rarity=True,
            package_path="tests",
            external_rank_providers=[RankProvider.TRAITS_SNIPER],
            filename="resolver/sample_files/bayc.json",
        )
        # Read the file and verify columns values are as expected for the given tokens
        output_filename = "testset_boredapeyachtclub.csv"

        rows = 0
        with open(output_filename) as csvfile:
            resolver_output_reader = csv.reader(csvfile)
            for idx, row in enumerate(resolver_output_reader):
                rows += 1
                if idx == 0:
                    assert row[0:10] == self.EXPECTED_COLUMNS
                else:
                    token_id = int(row[1])
                    if token_id in self.bayc_token_ids_to_ranks:
                        assert row[0] == "boredapeyachtclub"
                        expected_ranks = self.bayc_token_ids_to_ranks[token_id]
                        assert row[2] == expected_ranks[RankProvider.TRAITS_SNIPER]
                        assert row[5] == expected_ranks[RankProvider.OR_ARITHMETIC]
                        assert (
                            row[9]
                            == expected_ranks[RankProvider.OR_INFORMATION_CONTENT]
                        )

        assert rows == 10_001

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="This tests depends on external API",
    )
    def test_resolve_collection_data_rarity_sniffer(self):
        # Have the resolver pull in BAYC rarity rankings from various sources
        # Just do a check to ensure the ranks from different providers are
        # as expected
        slug_to_rows = resolve_collection_data(
            resolve_remote_rarity=True,
            package_path="tests",
            external_rank_providers=[RankProvider.RARITY_SNIFFER],
            filename="resolver/sample_files/bayc.json",
            output_file_to_disk=False,
        )
        rows = slug_to_rows["boredapeyachtclub"]

        for row in rows:
            token_id = int(row[1])
            if token_id in self.bayc_token_ids_to_ranks:
                assert row[0] == "boredapeyachtclub"
                expected_ranks = self.bayc_token_ids_to_ranks[token_id]
                assert str(row[3]) == expected_ranks[RankProvider.RARITY_SNIFFER]

        assert len(rows) == 10_000

    @pytest.mark.skipif(
        "not config.getoption('--run-resolvers')",
        reason="Needs OpenSea API key to be set up",
    )
    def test_resolve_collection_data_no_external(self):
        # Have the resolver pull in BAYC rarity rankings from various sources
        # Just do a check to ensure the ranks from different providers are
        # as expected
        resolve_collection_data(
            resolve_remote_rarity=True,
            package_path="tests",
            external_rank_providers=[],
            filename="resolver/sample_files/bayc.json",
        )
        # Read the file and verify columns values are as expected for the given tokens
        output_filename = "testset_boredapeyachtclub.csv"

        rows = 0
        with open(output_filename) as csvfile:
            resolver_output_reader = csv.reader(csvfile)
            for idx, row in enumerate(resolver_output_reader):
                rows += 1
                if idx == 0:
                    assert row[0:10] == self.EXPECTED_COLUMNS
                else:
                    token_id = int(row[1])
                    if token_id in self.bayc_token_ids_to_ranks:
                        assert row[0] == "boredapeyachtclub"
                        expected_ranks = self.bayc_token_ids_to_ranks[token_id]
                        assert (
                            row[9]
                            == expected_ranks[RankProvider.OR_INFORMATION_CONTENT]
                        )
                    if token_id in self.ic_bayc_token_ids_to_ranks:
                        assert row[9] == self.ic_bayc_token_ids_to_ranks[token_id]

        assert rows == 10_001
