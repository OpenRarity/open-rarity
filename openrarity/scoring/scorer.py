from openrarity.models.collection import Collection
from openrarity.models.token import Token

Score = float

class Scorer:
    """Base Scorer class
    Can implement various scoring strategies by implementing this interface
    """

    def score_token(self, collection: Collection, token: Token, normalized: bool = True) -> Score:
        """Scores an individual token based on the traits distribution across the whole collection

        Returns:
            float: The score of the token
        """
        raise NotImplementedError

    # Sub-classers: can override w/ more efficient methods

    def score_tokens(
        self, collection: Collection, tokens: list[Token], normalized: bool = True
    ) -> list[Score]:
        """Used if you only want to score a batch of tokens that belong to collection.

        Args:
            collection (Collection): The collection to score from
            tokens (list[Token]): a batch of tokens belonging to collection
                to be scored
            normalized (bool, optional): _description_. Defaults to True.

        Returns:
            list[Score]: list of scores in order of `tokens`
        """
        return [self.score_token(collection, t, normalized) for t in tokens]

    def score_collection(
        self, collection: Collection, normalized: bool = True
    ) -> list[Score]:
        """Scores all tokens on collection.tokens

        Returns:
            list[Score]: list of scores in order of `collection.tokens`
        """
        return self.score_tokens(collection, collection.tokens, normalized)

    def score_collections(
        self, collections: list[Collection], normalized: bool = True
    ) -> list[list[Score]]:
        return [self.score_collection(c, normalized) for c in collections]
