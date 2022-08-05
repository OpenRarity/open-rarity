from open_rarity.models.collection import Collection
from open_rarity.models.token import Token

Score = float


class Scorer:
    """Scorer class interface for different scoring algorithms to implement.
    Sub-classes are responsibile to ensure the batch functions are efficient for their particular algorithm.
    """

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> Score:
        """Scores an individual token based on the traits distribution across the whole collection

        Returns:
            float: The score of the token
        """
        raise NotImplementedError

    def score_tokens(self, collection: Collection, tokens: list[Token], normalized: bool = True) -> list[Score]:
        """Used if you only want to score a batch of tokens that belong to collection.
        This will typically be more efficient than calling score_token for each token in `tokens`.

        Args:
            collection (Collection): The collection to score from
            tokens (list[Token]): a batch of tokens belonging to collection
                to be scored
            normalized (bool, optional): _description_. Defaults to True.

        Returns:
            list[Score]: list of scores in order of `tokens`
        """
        raise NotImplementedError

    def score_collection(self, collection: Collection, normalized: bool = True) -> list[Score]:
        """Scores all tokens on collection.tokens

        Returns:
            list[Score]: list of scores in order of `collection.tokens`
        """
        return self.score_tokens(collection, collection.tokens, normalized)

    def score_collections(self, collections: list[Collection], normalized: bool = True) -> list[list[Score]]:
        return [self.score_collection(c, normalized) for c in collections]