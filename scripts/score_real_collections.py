import argparse
from open_rarity import RarityRanker
from open_rarity.models.token_rarity import TokenRarity
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
    default="score_real_collections_results",
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

parser.add_argument(
    "--cache",
    action=argparse.BooleanOptionalAction,
    dest="use_cache",
    default=True,
    help="Determines whether we force refetch all Token and trait data "
    "from Opensea or read data from a local cache file",
)

parser.add_argument(
    "--trait_count",
    action=argparse.BooleanOptionalAction,
    dest="add_trait_count",
    default=False,
    help="Determines whether we add TraitCount or not",
)


def score_collection_and_output_results(
    slug: str,
    output_filename: str,
    use_cache: bool,
    add_trait_count: bool = False,
):
    # Get collection
    collection = get_collection_from_opensea(
        slug, add_trait_count=add_trait_count, use_cache=use_cache
    )
    print(
        f"\nCreated collection {slug} with {collection.token_total_supply} tokens"
    )
    print(f"\n{collection.attributes_frequency_counts=}")
    print(f"\n\n{collection.tokens[0]} {collection.tokens[0].metadata=}")
    print(f"\n\n{collection.tokens[-1]} {collection.tokens[-1].metadata=}")

    # Score, rank  and sort ascending by token rarity rank
    sorted_token_rarities: list[TokenRarity] = RarityRanker.rank_collection(
        collection=collection
    )

    # Print out ranks and scores
    print("\nToken ID and their ranks and scores, sorted by rank")
    json_output = {}
    csv_rows = []
    for rarity_token in sorted_token_rarities:
        token_id = rarity_token.token.token_identifier.token_id
        rank = rarity_token.rank
        score = rarity_token.score
        json_output[token_id] = {"rank": rank, "score": score}
        csv_rows.append([token_id, rank, score])

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
    filename being "score_real_collections_results.json".

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
        `python -m scripts.score_real_collections`

        If you want to set your own slugs to process, you may pass it in via
        command-line.
        Example:
        `python -m scripts.score_real_collections boredapeyachtclub proof-moonbirds`
    """
    args = parser.parse_args()
    use_cache = args.use_cache
    filename_prefix = args.filename_prefix
    if args.add_trait_count:
        filename_prefix = f"{filename_prefix}_trait_count"
    print(f"Scoring collections: {args=}")
    print(f"Output file prefix: {filename_prefix} with type .{args.filetype}")

    files = []
    for slug in args.slugs:
        output_filename = f"{filename_prefix}_{slug}.{args.filetype}"
        print(f"Generating results for: {slug}")
        score_collection_and_output_results(
            slug=slug,
            output_filename=output_filename,
            use_cache=use_cache,
            add_trait_count=args.add_trait_count,
        )
        print(f"Outputted results to: {output_filename}")
        files.append(output_filename)

    print("Finished scoring and ranking collections. Output files:")
    for file in files:
        print(f"\t{file}")
