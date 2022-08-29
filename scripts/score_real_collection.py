from open_rarity import OpenRarityScorer
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_from_opensea,
)
from open_rarity.resolver.testset_resolver import extract_rank

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

    # Convert scores to rank
    token_id_to_rank_score = extract_rank(
        token_id_to_scores={
            token_id: score for token_id, score in enumerate(token_scores)
        }
    )

    # Print out ranks and scores
    for token_id, rank_score in token_id_to_rank_score.items():
        print(
            f"\tToken {token_id} has rank {rank_score[0]} score: {rank_score[1]}"
        )
