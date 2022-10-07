from open_rarity import Collection, OpenRarityScorer, Token
from open_rarity.rarity_ranker import RarityRanker

if __name__ == "__main__":
    scorer = OpenRarityScorer()

    collection = Collection(
        name="My Collection Name",
        tokens=[
            Token.from_erc721(
                contract_address="0xa3049...",
                token_id=1,
                metadata_dict={"hat": "cap", "shirt": "blue"},
            ),
            Token.from_erc721(
                contract_address="0xa3049...",
                token_id=2,
                metadata_dict={"hat": "visor", "shirt": "green"},
            ),
            Token.from_erc721(
                contract_address="0xa3049...",
                token_id=3,
                metadata_dict={"hat": "visor", "shirt": "blue"},
            ),
        ],
    )  # Replace inputs with your collection-specific details here

    # Generate scores for a collection
    token_scores = scorer.score_collection(collection=collection)

    print(f"Token scores for collection: {token_scores}")

    # Generate score for a single token in a collection
    token = collection.tokens[0]  # Your token details filled in
    token_score = scorer.score_token(collection=collection, token=token)

    # Better yet.. just use ranker directly!
    ranked_tokens = RarityRanker.rank_collection(collection=collection)
    for ranked_token in ranked_tokens:
        print(
            f"Token {ranked_token.token} has rank {ranked_token.rank} "
            "and score {ranked_token.score}"
        )
