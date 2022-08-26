from open_rarity import OpenRarityScorer
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_from_opensea,
)

if __name__ == "__main__":
    """This script fetches bored ape yacht club collection and token metadata
    from the Opensea API via opensea_api_helpers and scores the
    collection via OpenRarity scorer.
    """
    scorer = OpenRarityScorer()
    slug = "boredapeyachtclub"

    # Get collection
    collection = get_collection_from_opensea(slug)
    print(f"Created collection with {collection.token_total_supply} tokens")

    # Score the entire collection
    token_scores = scorer.score_collection(collection=collection)
    print(
        f"Calculated {len(token_scores)} token scores for collection: {slug}"
    )

    # Print out scores
    for i, token_score in enumerate(token_scores):
        print(f"\tToken {collection.tokens[i]} has score: {token_score}")

    # Generate score for a single token in a collection
    token = collection.tokens[0]
    token_score = scorer.score_token(
        collection=collection, token=token, normalized=True
    )

    print(f"Token {token} has score: {token_score}")
