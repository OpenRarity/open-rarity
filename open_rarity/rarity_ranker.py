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
            sorted by rank
        """

        if (
            collection is None
            or collection.tokens is None
            or len(collection.tokens) == 0
        ):
            return []

        tokens = collection.tokens
        scores: list[float] = scorer.score_tokens(collection, tokens=tokens)

        # fail ranking if dimension of scores doesn't match dimension of tokens
        assert len(tokens) == len(scores)

        token_rarities: list[TokenRarity] = []
        # augment collection tokens with score information
        for idx, token in enumerate(tokens):
            token_rarities.append(TokenRarity(token=token, score=scores[idx]))

        return RarityRanker.set_rarity_ranks(token_rarities)

    @staticmethod
    def set_rarity_ranks(
        token_rarities: list[TokenRarity],
    ) -> list[TokenRarity]:
        """Ranks a set of tokens Scores that are higher indicate a higher rarity,
        and thus a lower rank.
        Tokens with the same score will be assigned the same rank, e.g. we use RANK
        (vs. DENSE_RANK).
        Example: 1, 2, 2, 2, 5.
        Scores are considered the same rank if they are within about 9 decimal digits
        of each other.

        Parameters
        ----------
        token_rarities : list[TokenRarity]
            unordered list of tokens with rarity score
            information that should have the ranks set on

        Returns
        -------
        list[TokenRarity]
            modified input token_rarities with ranking data set,
            ordered by rank ascending and score descending

        """
        sorted_token_rarities: list[TokenRarity] = sorted(
            token_rarities,
            key=lambda k: k.score,
            reverse=True,
        )

        # perform ranking of each token in collection
        for i, token in enumerate(sorted_token_rarities):
            rank = i + 1
            if i > 0:
                prev_token = sorted_token_rarities[i - 1]
                scores_equal = math.isclose(token.score, prev_token.score)
                if scores_equal:
                    rank = prev_token.rank

            token.rank = rank

        return sorted_token_rarities
