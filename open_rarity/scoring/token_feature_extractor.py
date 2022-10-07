from open_rarity.models import Token
from open_rarity.models.collection import Collection
from open_rarity.models.token_ranking_features import TokenRankingFeatures


class TokenFeatureExtractor:
    """
    Utility class that extract features from tokens
    """

    @staticmethod
    def extract_unique_attribute_count(
        token: Token, collection: Collection
    ) -> TokenRankingFeatures:
        """This method extracts unique attributes count from the token

        Parameters
        ----------
        token : Token
            The token to extract features from
        collection : Collection
            The collection with the attributes frequency counts to base the
            token trait probabilities on to calculate score.

        Returns
        -------
        TokenFeatures
            Token features wrapper class that contains extracted features

        """

        unique_attributes_count: int = 0

        for string_attribute in token.metadata.string_attributes.values():
            count = collection.total_tokens_with_attribute(string_attribute)

            if count == 1:
                unique_attributes_count += 1

        return TokenRankingFeatures(unique_attribute_count=unique_attributes_count)
