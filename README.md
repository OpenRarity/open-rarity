![OpenRarity](img/OR_Github_banner.jpg)

[![Version][version-badge]][version-link]
[![Test CI][ci-badge]][ci-link]
[![License][license-badge]][license-link]


# OpenRarity

We’re excited to announce OpenRarity(Beta), a new rarity protocol we’re building for the NFT community. Our objective is to provide a transparent rarity calculation that is entirely open-source, objective, and reproducible.

With the explosion of new collections, marketplaces and tooling in the NFT ecosystem, we realized that rarity ranks often differed across platforms which could lead to confusion for buyers, sellers and creators. We believe it’s important to find a way to provide a unified and consistent set of rarity rankings across all platforms to help build more trust and transparency in the industry.

We are releasing the OpenRarity library in a Beta preview to crowdsource feedback from the community and incorporate it into the library evolution.

See the full announcement in the [blog post](https://mirror.xyz/openrarity.eth/LUoJnybWuNYedIQHD6RRdX1SS9MiowdI6a69X-lefGM)

# Surprisal Ranking Algorithm

[Information content](https://en.wikipedia.org/wiki/Information_content) is an alternative way of expressing probabilities that is more well suited for assessing rarity. Think of it as a measure of how surprised someone would be upon discovering something.

1. Probabilities of 1 (i.e. every single token has the Trait) convey no rarity and add zero information to the score.
2. As the probability approaches zero (i.e. the Trait becomes rarer), the information content continues to rise with no bound. See equation below for explanation.
3. It is valid to perform linear operations (e.g. addition or arithmetic mean) on information, but not on raw probabilities.

Information content is used to solve lots of problems that involve something being unlikely (i.e. rare or scarce). [This video shows how it was used to solve Wordle](https://www.youtube.com/watch?v=v68zYyaEmEA) and also has an explanation of the equations, along with graphics to make it easier to understand. You can [skip straight to the part on information theory](https://youtu.be/v68zYyaEmEA?t=485) if you’d like.

The score is defined as:

$$
\frac{I(x)}{\mathbb{E}[I(x)]} \textrm{ where } I(x) = \sum_{i=1}^n-\log_2(P(trait_i))
$$

This can look daunting, so let’s break it down:

- $P(trait)$ simply means the probability of an NFT having a specific trait within the entire collection. When calculating this value for NFTs without any value for a trait, we use an implicit “null” trait as if the creator had originally marked them as “missing”.
- $-log_2(P(trait))$ is the mathematical way to calculate how many times you’d have to split the collection in half before you reach a trait that’s just as rare. Traits that occur in half of the NFTs get 1 point, those that occur in a quarter of the NFTs get 2 points, and so on. Using the $-log_2$ is just a way to account for the spaces in between whole-number points, like assigning 1.58 points to traits that occur in every third NFT.
  - Each of these points is actually called a “bit” of information.
  - The important thing is that even if there was a one-off grail in an impossibly large NFT collection, we could keep assigning points!
  - Conversely, if a trait exists on every NFT, i.e. $P(trait)=1$, then it's perfectly unsurprising because $-log_2(1) = 0$.
  - Unlike with probabilities, it’s valid to add together bits of information.
- $\Sigma$ is the Greek letter sigma (like an English S), which means “sum of”. Mathematicians like to be rigorous so the $i$ and the $n$ tell us exactly what to sum up, but really just means “add up the points for each of the NFT's traits”.
- $\mathbb{E}[I(x)]$ is the “expected value”, which is a weighted average of the information of all the NFTs in the collection, the weighting done by probability. Because this a collection-wide value, it doesn’t change the ranking nor the relative rarity scores, it just squishes them closer. We include it because it normalizes the scores for collections that have lots and lots of traits—these will have a higher $I(x)$ rarity score for each NFT, but will also have a higher $\mathbb{E}[I(x)]$ across the collection so they cancel each other out and make it fairer to compare between collections.

# Library Design
OpenRarity consists of two core parts: **Runtime** and **Rarity Resolver**.

The **Runtime** part of the library can be integrated into any Python 3.10+ application to perform the scoring of any collection. The runtime doesn’t resolve collections metadata—it’s the responsibility of an application to provide correct metadata to perform collection scoring.

The **Rarity Resolver** is a tool to compare rarity ranks across various providers,
including various OpenRarity algorithms.

## Runtime - Using the library
Here is a generic way of using the OpenRarity scoring interface:
```
from open_rarity import Collection, Token, RarityScorer

scorer = RarityScorer()
# Your collection details below
collection = Collection()

# Generate scores for a collection
token_scores = scorer.score_collection(collection=collection)

# Generate score for a single token in a collection
token = collection.tokens[0]
token_score = scorer.score_token(collection=collection, token=token, normalized=True)
```

In order to generate the Token and Collection, you will need to properly set the attributes distribution on the collection and the individual attributes belonging to each token. You may either have these details on hand or fetch them through an API. Example of how we do it in order to compare rarity scores across providers live in testset_resolver.py, which leverages the data returned by the opensea API (see opensea_api_helpers.py) to construct the Token and Collection object.

For an actual runnable demo script that does this, checkout scripts/score_generated_collection.py.
In shell run:
```
python -m scripts.score_generated_collection
```

For a sample of how to use the existing Opensea API to fetch the collection and token
metadata and to funnel that into the scoring library, checkout scripts/score_real_collections.
In shell run:
```
python -m scripts.score_real_collections
```
This may also be used to generate json or csv outputs of OpenRarity scoring and ranks for any number of collections
```
python -m scripts.score_real_collections boredapeyachtclub proof-moonbirds
```


## Rarity Resolver
You may use the rarity resolver tool to either view ranking scores across providers, or to debug any collections scoring. Follow these steps to score the collection with the tool (by calling OpenSea API):

- Curate the <a href="https://github.com/ProjectOpenSea/open-rarity/blob/main/open_rarity/data/test_collections.json" title=“Collections>collections list </a> you want to score with OpenRarity
- Provide your <a href="https://github.com/ProjectOpenSea/open-rarity/blob/main/open_rarity/resolver/opensea_api_helpers.py#L20"> OpenSea API Key </a>
- Run scoring for these collections with the following command:

    ```python
    python -m open_rarity.resolver.testset_resolver # without external rarity resolution
    python -m open_rarity.resolver.testset_resolver external # with external rarity resolution
    ```
- Inspect scorring log file and csv files with ranking result

Alternatively, if you just want to generate OpenRarity scoring only, and not do rank comparisons, and output to a json, you may run:
```
python -m scripts.score_real_collections <slugs>
```
Example:
```
python -m scripts.score_real_collections boredapeyachtclub proof-moonbirds
```

## Running tests locally

```
poetry install # install dependencies locally
poetry run pytest # run tests
```

Some tests are skipped by default due to it being more integration/slow tests.
To run resolver tests:
```
poetry run pytest -k test_testset_resolver --run-resolvers
```

# Contributions guide and governance

OpenRarity is a cross-company effort to improve rarity computation for NFTs (Non-Fungible Tokens). The core collaboration group consists of four primary contributors: Curio, icy.tools, OpenSea and Proof

OpenRarity is an open-source project and all contributions are welcome. Consider following steps when you request/propose contribution:

- Have a question? Submit it on OpenRarity GitHub  [discussions](https://github.com/ProjectOpenSea/open-rarity/discussions) page
- Create GitHub issue/bug with description of the problem [link](https://github.com/ProjectOpenSea/open-rarity/issues/new?assignees=impreso&labels=bug&template=bug_report.md&title=)
- Submit Pull Request with proposed changes
- To merge the change in the `main` branch you required to get at least 2 approvals from the project maintainer list
- Always add a unit test with your changes

We use git-precommit hooks in OpenRarity repo. Install it with the following command
```
poetry run pre-commit install
```

# Project Setup and Core technologies

We used the following core technologies in OpenRarity:

- Python ≥ 3.10.x
- Poetry for dependency management
- Numpy ≥1.23.1
- PyTest for unit tests

# License

Apache 2.0 , OpenSea, ICY, Curio, PROOF



[license-badge]: https://img.shields.io/github/license/ProjectOpenSea/open-rarity
[license-link]: https://github.com/ProjectOpenSea/open-rarity/blob/main/LICENSE
[ci-badge]: https://github.com/ProjectOpenSea/open-rarity/actions/workflows/tests.yaml/badge.svg
[ci-link]: https://github.com/ProjectOpenSea/open-rarity/actions/workflows/tests.yaml
[version-badge]: https://img.shields.io/github/v/release/ProjectOpenSea/open-rarity
[version-link]: https://github.com/ProjectOpenSea/open-rarity/releases?display_name=tag
