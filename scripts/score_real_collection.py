from open_rarity import OpenRarityScorer
from open_rarity import RarityRanker
from open_rarity.models.token import Token
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

    # Print out ranks and scores
    token_id_to_ranks = RarityRanker.rank_collection(collection=collection)

    print("Token ID and their ranks and scores, sorted by rank")
    tokens_with_rarity = collection.tokens

    sorted_tokens: list[Token] = sorted(
        tokens_with_rarity, key=lambda t: t.token_rarity.rank
    )

    for token in sorted_tokens:
        print(
            f"\tToken {token.token_identifier.token_id}"
            f"rank: {token.token_rarity.rank} "
            f"score: {token.token_rarity.score}"
        )
