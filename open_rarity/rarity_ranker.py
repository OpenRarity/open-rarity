import math


class RarityRanker:
    """This class is used to rank a set of tokens given their rarity scores."""

    @staticmethod
    def rank_tokens(*, token_id_to_scores: dict[str, float]) -> dict[str, int]:
        """Ranks a set of tokens, identified uniquely by a string, based on
        the scores provided. The ranking is done assuming @token_id_to_scores
        contains all tokens for a given cohort/collection to rank tokens for.
        Scores that are higher indicate a higher rarity, and thus a lower rank.

        Tokens with the same score will be assigned the same rank, e.g. we use RANK
        (vs. DENSE_RANK).
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same rank if they are within about 9 decimal digits
        of each other.


        Parameters
        ----------
        token_ids_to_score : dict[str, float]
            A dictionary of token ids (this can be whatever id you want, as long
            as its unique) to the rarity score.

        Returns
        -------
        dict[str, int]
            A dictionary of token ids to their ranks. More specificially, it is the
            provided tokens ids to the rank it has within the set of possible
            tokens defined by @token_id_to_scores.
        """
        sorted_token_ids = sorted(
            token_id_to_scores.keys(),
            key=lambda k: token_id_to_scores[k],
            reverse=True,
        )
        token_id_to_rank = {}

        for i, token_id in enumerate(sorted_token_ids):
            rank = i + 1
            if i > 0:
                prev_token_id = sorted_token_ids[i - 1]
                scores_equal = math.isclose(
                    token_id_to_scores[token_id],
                    token_id_to_scores[prev_token_id],
                )
                if scores_equal:
                    rank = token_id_to_rank[prev_token_id]

            token_id_to_rank[token_id] = rank

        return token_id_to_rank
