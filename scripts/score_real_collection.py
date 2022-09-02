import argparse
from open_rarity import OpenRarityScorer
from open_rarity import RarityRanker
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_from_opensea,
)
import json
import csv

parser = argparse.ArgumentParser()
parser.add_argument(
    "slugs",
    type=str,
    default=["boredapeyachtclub"],
    nargs="*",
    help="Slugs you want to generate scoring for, separated by spaces",
)
parser.add_argument(
    "--filename_prefix",
    dest="filename_prefix",
    default="score_real_collection_results",
    help="The filename prefix to output the ranking results to. "
    "The filename will be {prefix}_{slug}.json/csv",
)

parser.add_argument(
    "--filetype",
    dest="filetype",
    default="json",
    choices=["json", "csv"],
    help="Determines output file type. Either 'json' or 'csv'.",
)


def score_collection_and_output(
    scorer: OpenRarityScorer, slug: str, output_filename: str
):
    # Get collection
    collection = get_collection_from_opensea(slug)
    print(
        f"Created collection {slug} with {collection.token_total_supply} tokens"
    )

    # Score the entire collection
    token_scores = scorer.score_collection(collection=collection)
    print(
        f"Calculated {len(token_scores)} token scores for collection: {slug}"
    )

    # Convert scores to rank
    token_id_to_scores = {
        str(token_id): score for token_id, score in enumerate(token_scores)
    }
    token_id_to_ranks = RarityRanker.rank_tokens(
        token_id_to_scores=token_id_to_scores
    )

    # Print out ranks and scores
    print("Token ID and their ranks and scores, sorted by rank")
    sorted_token_ids = sorted(
        token_id_to_ranks.keys(), key=lambda tid: token_id_to_ranks[tid]
    )
    json_output = {}
    csv_rows = []
    for token_id in sorted_token_ids:
        rank = token_id_to_ranks[token_id]
        score = token_id_to_scores[token_id]
        json_output[token_id] = {"rank": rank, "score": score}
        csv_rows.append([token_id, rank, score])
        print(f"\tToken {token_id} has rank {rank} score: {score}")

    # Write to json
    if output_filename.endswith(".json"):
        with open(output_filename, "w") as jsonfile:
            json.dump(json_output, jsonfile, indent=4)

    # Write to csv
    if output_filename.endswith(".csv"):
        with open(output_filename, "w") as csvfile:
            writer = csv.writer(csvfile)
            # headers
            writer.writerow(["token_id", "rank", "score"])
            # content
            writer.writerows(csv_rows)


if __name__ == "__main__":
    """This script by default fetches bored ape yacht club collection and token
    metadata from the Opensea API via opensea_api_helpers and scores + ranks the
    collection via OpenRarity scorer.

    It will output results into {prefix}_{slug}.json/csv file, with the default
    filename being "score_real_collection_results.json".

    If JSON, format is:
    {
        <token_id>: {
            "rank": <int>,
            "score": <float>,
        }
    }

    If CSV, format is:
    Columns: Token ID, Rank, Score

    Command:
        `python -m scripts.score_real_collection`

        If you want to set your own slugs to process, you may pass it in via
        command-line.
        Example:
        `python -m scripts.score_real_collection boredapeyachtclub proof-moonbirds`
    """
    args = parser.parse_args()
    print(f"Scoring collections: {args.slugs}")
    print(
        f"Output file prefix: {args.filename_prefix} with type {args.filetype}"
    )

    scorer = OpenRarityScorer()
    files = []
    for slug in args.slugs:
        output_filename = f"{args.filename_prefix}_{slug}.{args.filetype}"
        print(f"Generating results for: {slug}")
        score_collection_and_output(
            scorer=scorer,
            slug=slug,
            output_filename=output_filename,
        )
        print(f"Outputted results to: {output_filename}")
        files.append(output_filename)

    print("Finished scoring and ranking collections. Output files:")
    for file in files:
        print(f"\t{file}")
