from abc import abstractmethod
from typing import Protocol

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token


class ScoringHandler(Protocol):
    """ScoringHandler class is an interface for different scoring algorithms to
    implement. Sub-classes are responsibile to ensure the batch functions are
    efficient for their particular algorithm.
    """

    @abstractmethod
    def score_token(self, collection: Collection, token: Token) -> float:
        """Scores an individual token based on the traits distribution across
        the whole collection.

        Parameters
        ----------
        collection : Collection
            The collection with the attributes frequency counts to base the
            token trait probabilities on to calculate score.
        token : Token
            The token to score

        Returns
        -------
        float
            The token score
        """
        raise NotImplementedError

    @abstractmethod
    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
    ) -> list[float]:
        """Used if you only want to score a batch of tokens that belong to collection.
        This will typically be more efficient than calling score_token for each
        token in `tokens`.

        Parameters
        ----------
        collection : Collection
            The collection to score from
        tokens : list[Token]
            a batch of tokens belonging to collection to be scored

        Returns
        -------
        list[float]
            list of scores in order of `tokens`
        """
        raise NotImplementedError
