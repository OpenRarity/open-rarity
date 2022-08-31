from open_rarity.rarity_ranker import RarityRanker


class TestRarityRanker:
    def test_rarity_ranker_empty(self) -> None:
        assert RarityRanker.rank_tokens(token_id_to_scores={}) == {}

    def test_rarity_ranker_one_item(self) -> None:
        assert RarityRanker.rank_tokens(
            token_id_to_scores={"Cat #10": 38492.1203}
        ) == {"Cat #10": 1}

    def test_rarity_ranker_unique_scores(self) -> None:
        token_ids_to_ranks = RarityRanker.rank_tokens(
            token_id_to_scores={
                "BAYC #1": 1239.120304,
                "BAYC #2": 1239.120302,
                "BAYC #3": 629.03948,
                "BAYC #4": 8038.302340,
            }
        )
        assert len(token_ids_to_ranks) == 4
        assert token_ids_to_ranks["BAYC #4"] == 1
        assert token_ids_to_ranks["BAYC #1"] == 2
        assert token_ids_to_ranks["BAYC #2"] == 3
        assert token_ids_to_ranks["BAYC #3"] == 4

    def test_rarity_ranker_same_scores(self) -> None:
        token_ids_to_ranks = RarityRanker.rank_tokens(
            token_id_to_scores={
                "BAYC #4": 8038.302340,
                "BAYC #2": 3049.30340,
                "BAYC #6": 1239.1203061,
                "BAYC #7": 1239.1203048,
                "BAYC #5": 1239.1203041,
                "BAYC #1": 1239.120304023,
                "BAYC #9": 1239.120303023,
                "BAYC #8": 1239.12,
                "BAYC #3": 629.03948,
            }
        )
        print(token_ids_to_ranks)
        assert len(token_ids_to_ranks) == 9
        assert token_ids_to_ranks["BAYC #4"] == 1
        assert token_ids_to_ranks["BAYC #2"] == 2
        assert token_ids_to_ranks["BAYC #6"] == 3
        assert token_ids_to_ranks["BAYC #7"] == 4
        assert token_ids_to_ranks["BAYC #5"] == 4
        assert token_ids_to_ranks["BAYC #1"] == 4
        assert token_ids_to_ranks["BAYC #9"] == 4
        assert token_ids_to_ranks["BAYC #8"] == 8
        assert token_ids_to_ranks["BAYC #3"] == 9
