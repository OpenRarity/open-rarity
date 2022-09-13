import math
from open_rarity.models.collection import Collection
from open_rarity.models.token_rarity import TokenRarity

from open_rarity.scoring.scorer import Scorer


class RarityRanker:
    """This class is used to rank a set of tokens given their rarity scores."""

    default_scorer = Scorer()

    @staticmethod
    def rank_collection(
        collection: Collection, scorer: Scorer = default_scorer
    ) -> list[TokenRarity]:
        """
        Ranks tokens in the collection with the default scorer implementation.
        Scores that are higher indicate a higher rarity, and thus a lower rank.

        Tokens with the same score will be assigned the same rank, e.g. we use RANK
        (vs. DENSE_RANK).
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same rank if they are within about 9 decimal digits
        of each other.


        Parameters
        ----------
        collection : Collection
            Collection object with populated tokens
        scorer: Scorer
            Scorer instance

        Returns
        -------
        list[TokenRarity]
            list of TokenRarity objects with score, rank and token information
        """

        if (
            collection is None
            or collection.tokens is None
            or len(collection.tokens) == 0
        ):
            return collection

        tokens = collection.tokens
        scores: list[float] = scorer.score_tokens(collection, tokens=tokens)

        # fail ranking if dimension of scores doesn't match dimension of tokens
        assert len(tokens) == len(scores)

        token_rarity_list: list[TokenRarity] = []
        # augment collection tokes with score information
        for idx, token in enumerate(tokens):
            token_rarity_list.append(
                TokenRarity(token=token, score=scores[idx])
            )

        return RarityRanker.rank_tokens(token_rarity_list)

    @staticmethod
    def rank_tokens(tokens: list[TokenRarity]) -> list[TokenRarity]:
        """Ranks a set of tokens Scores that are higher indicate a higher rarity,
        and thus a lower rank.
        Tokens with the same score will be assigned the same rank, e.g. we use RANK
        (vs. DENSE_RANK).
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same rank if they are within about 9 decimal digits
        of each other.

        Parameters
        ----------
        tokens : list[TokenRarity]
            unordered list of tokens with rarity score information

        Returns
        -------
        tokens: list[TokenRarity]
            list of tokens with rarity scores sorted by rank

        """
        sorted_tokens_by_score: list[TokenRarity] = sorted(
            tokens,
            key=lambda k: k.score,
            reverse=True,
        )

        # perform ranking of each token in collection
        for i, token in enumerate(sorted_tokens_by_score):
            rank = i + 1
            if i > 0:
                prev_token = sorted_tokens_by_score[i - 1]
                scores_equal = math.isclose(token.score, prev_token.score)
                if scores_equal:
                    rank = prev_token.rank

            token.rank = rank

        return sorted_tokens_by_score
