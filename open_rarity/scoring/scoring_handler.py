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
    def score_token(
        self, collection: Collection, token: Token, normalized: bool = True
    ) -> float:
        """Scores an individual token based on the traits distribution across
        the whole collection.

        Returns:
            float: The score of the token
        """
        raise NotImplementedError

    @abstractmethod
    def score_tokens(
        self,
        collection: Collection,
        tokens: list[Token],
        normalized: bool = True,
    ) -> list[float]:
        """Used if you only want to score a batch of tokens that belong to collection.
        This will typically be more efficient than calling score_token for each
        token in `tokens`.

        Args:
            collection (Collection): The collection to score from
            tokens (list[Token]): a batch of tokens belonging to collection
                to be scored
            normalized (bool, optional): _description_. Defaults to True.

        Returns:
            list[Score]: list of scores in order of `tokens`
        """
        raise NotImplementedError
