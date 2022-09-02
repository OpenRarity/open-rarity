from open_rarity import OpenRarityScorer
from open_rarity import RarityRanker
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_from_opensea,
)

if __name__ == "__main__":
    """This script fetches bored ape yacht club collection and token metadata
    from the Opensea API via opensea_api_helpers and scores the
    collection via OpenRarity scorer.

    Command: `python -m scripts.score_real_collection`
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
    token_id_to_scores = {
        str(token_id): score for token_id, score in enumerate(token_scores)
    }

    # Print out ranks and scores
    print("Token ID and their ranks and scores, sorted by token ID")
    token_id_to_ranks = RarityRanker.rank_tokens(
        token_id_to_scores=token_id_to_scores
    )
    for token_id in range(collection.token_total_supply):
        token_key = str(token_id)
        print(
            f"\tToken {token_id} has rank {token_id_to_ranks[token_key]} "
            f"score: {token_id_to_scores[token_key]}"
        )

    print("Token ID and their ranks and scores, sorted by rank")
    sorted_token_ids = sorted(
        token_id_to_ranks.keys(), key=lambda tid: token_id_to_ranks[tid]
    )
    for token_id in sorted_token_ids:
        print(
            f"\tToken {token_id} has rank {token_id_to_ranks[token_id]} "
            f"score: {token_id_to_scores[token_id]}"
        )
