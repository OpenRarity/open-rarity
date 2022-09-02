from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_standard import TokenStandard
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from open_rarity.scoring.scoring_handler import ScoringHandler


class Scorer:
    """Scorer is the main class to score rarity scores for a given
    collection and token(s) based on the default OpenRarity scoring
    algorithm.
    """

    handler: ScoringHandler

    def __init__(self) -> None:
        # OpenRarity uses InformationContent as the scoring algorithm of choice.
        self.handler = InformationContentScoringHandler()

    def validate_collection(self, collection: Collection) -> None:
        """Validate collection eligibility for OpenRarity scoring

        Parameters
        ----------
        collection: Collection)
            The collection to validate
        """
        if collection.has_numeric_attribute:
            raise ValueError(
                "OpenRarity currently does not support collections with "
                "numeric or date traits"
            )

        if collection.token_standards != [TokenStandard.ERC721]:
            raise ValueError(
                "OpenRarity currently does not support non-ERC721 collections"
            )

    def score_token(self, collection: Collection, token: Token) -> float:
        """Scores an individual token based on the traits distribution across
        the whole collection.

        Parameters
        ----------
        collection : Collection
            The collection to score from
        token : Token
            a single Token to score

        Returns
        -------
        float
            The score of the token
        """
        self.validate_collection(collection=collection)
        return self.handler.score_token(collection=collection, token=token)

    def score_tokens(
        self, collection: Collection, tokens: list[Token]
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
        self.validate_collection(collection=collection)
        return self.handler.score_tokens(collection=collection, tokens=tokens)

    def score_collection(self, collection: Collection) -> list[float]:
        """Scores all tokens on collection.tokens

        Parameters
        ----------
        collection : Collection
            The collection to score all tokens from

        Returns
        -------
        list[float]
            list of scores in order of `collection.tokens`
        """
        self.validate_collection(collection=collection)
        return self.handler.score_tokens(
            collection=collection,
            tokens=collection.tokens,
        )

    def score_collections(
        self, collections: list[Collection]
    ) -> list[list[float]]:
        """Scores all tokens in every collection provided.

        Parameters
        ----------
        collections: list[Collection])
            The collections to score

        Returns
        -------
        list[list[float]]
            A list of scores for all tokens in each given Collection,
            ordered by the collection's `tokens` field.
        """
        for collection in collections:
            self.validate_collection(collection=collection)
        return [
            self.handler.score_tokens(collection=c, tokens=c.tokens)
            for c in collections
        ]
