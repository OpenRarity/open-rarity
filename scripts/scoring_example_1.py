from open_rarity import (
    Collection,
    EVMContractTokenIdentifier,
    RarityScorer,
    StringAttribute,
    Token,
    TokenMetadata,
    TokenStandard,
)

if __name__ == "__main__":
    scorer = RarityScorer()
    # A collection of 2 tokens
    collection = Collection(
        name="My Collection Name",
        attributes_frequency_counts={
            "hat": {"cap": 1, "visor": 2},
            "shirt": {"blue": 2, "green": 1},
        },
        tokens=[
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0xa3049...", token_id=1
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat": StringAttribute(name="hat", value="cap"),
                        "shirt": StringAttribute(name="shirt", value="blue"),
                    }
                ),
            ),
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0xa3049...", token_id=2
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat": StringAttribute(name="hat", value="visor"),
                        "shirt": StringAttribute(name="shirt", value="green"),
                    }
                ),
            ),
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0xa3049...", token_id=3
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes={
                        "hat": StringAttribute(name="hat", value="visor"),
                        "shirt": StringAttribute(name="shirt", value="blue"),
                    }
                ),
            ),
        ],
    )  # Replace inputs with your collection-specific details here

    # Generate scores for a collection
    token_scores = scorer.score_collection(collection=collection)

    print(f"Token scores for collection: {token_scores}")

    # Generate score for a single token in a collection
    token = collection.tokens[0]  # Your token details filled in
    token_score = scorer.score_token(
        collection=collection, token=token, normalized=True
    )

    print(f"Token score: {token_score}")
