import math
from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_rarity import TokenRarity

from open_rarity.scoring.scorer import Scorer


class RarityRanker:
    """This class is used to rank a set of tokens given their rarity scores."""

    default_scorer = Scorer()

    @staticmethod
    def rank_collection(
        collection: Collection, scorer: Scorer = default_scorer
    ) -> Collection:
        """
        Ranks tokens in the collection with the default scorer implementation.
        Scores that are higher indicate a higher rarity, and thus a lower rank.

        Tokens with the same score will be assigned the same rank.
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same if they are within about 9 decimal digits
        of each other.


        Parameters
        ----------
        collection : Collection
            OpenRarity collection object with populated tokens
        scorer: Scorer
            Scorer instance that specifies the formula

        Returns
        -------
        Collection
            A collection with the populated rarity data
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

        # augment collection tokes with score information
        for idx, token in enumerate(tokens):
            token.token_rarity = TokenRarity(score=scores[idx])

        # assign sorted tokens list to the collection object
        collection.tokens = RarityRanker.rank_tokens(collection.tokens)

        return collection

    @staticmethod
    def rank_tokens(tokens: list[Token]) -> dict[str, int]:
        """Ranks a set of tokens Scores that are higher indicate a higher rarity,
        and thus a lower rank.
        Tokens with the same score will be assigned the same rank, e.g. we use RANK
        (vs. DENSE_RANK).
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same rank if they are within about 9 decimal digits
        of each other.

        Parameters
        ----------
        tokens : list[Token]
            unordered list of tokens with rarity score information

        Returns
        -------
        tokens: list[Token]

        """
        sorted_tokens_by_score: list[Token] = sorted(
            tokens,
            key=lambda k: k.token_rarity.score,
            reverse=True,
        )

        # perform ranking of each token in collection
        for i, token in enumerate(sorted_tokens_by_score):
            rank = i + 1
            if i > 0:
                prev_token = sorted_tokens_by_score[i - 1]
                scores_equal = math.isclose(
                    token.token_rarity.score, prev_token.token_rarity.score
                )
                if scores_equal:
                    rank = prev_token.token_rarity.rank

            token.token_rarity.rank = rank

        return sorted_tokens_by_score
