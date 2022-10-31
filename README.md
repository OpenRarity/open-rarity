![OpenRarity](img/OR_Github_banner.jpg)

[![Version][version-badge]][version-link]
[![Test CI][ci-badge]][ci-link]
[![License][license-badge]][license-link]


# OpenRarity

We’re excited to announce OpenRarity, a new rarity protocol we’re building for the NFT community. Our objective is to provide a transparent rarity calculation that is entirely open-source, objective, and reproducible.

With the explosion of new collections, marketplaces and tooling in the NFT ecosystem, we realized that rarity ranks often differed across platforms which could lead to confusion for buyers, sellers and creators. We believe it’s important to find a way to provide a unified and consistent set of rarity rankings across all platforms to help build more trust and transparency in the industry.

We are releasing the OpenRarity library in a Beta preview to crowdsource feedback from the community and incorporate it into the library evolution.

See the full announcement in the [blog post](https://mirror.xyz/openrarity.eth/LUoJnybWuNYedIQHD6RRdX1SS9MiowdI6a69X-lefGM).

## CLI Usage


If you already have a json file containing the metadata for the tokens you want to rank you can run the following which will print ranks to stdout.

```
❯ openrarity rank data/boredapeyachtclub/tokens.json | head -n 10
  token_id    unique_traits       ic    rank
----------  ---------------  -------  ------
      7495                0  42.0592       1
      4873                0  40.4554       2
      8854                0  40.2091       3
       446                0  40.017        4
        73                0  39.6501       5
      8135                0  39.5842       6
      8976                0  39.5072       7
      4980                0  39.4849       8
```

Likewise you can write to a json file
```
❯ openrarity rank data/boredapeyachtclub/tokens.json -o boredapeyachtclub_ranks.json
```


If you don't have metadata available you can fetch it from OpenSea first
```
❯ openrarity opensea fetch-assets --slug boredapeyachtclub --start-token-id 0 --end-token-id 9999 --rank | head -n 10
100%|████████████████████████████████████████| 334/334 [01:40<00:00,  3.33it/s]
  token_id    unique_traits       ic    rank
----------  ---------------  -------  ------
      7495                0  42.0592       1
      4873                0  40.4554       2
      8854                0  40.2091       3
       446                0  40.017        4
        73                0  39.6501       5
      8135                0  39.5842       6
      8976                0  39.5072       7
      4980                0  39.4849       8
```

# Developer documentation

Read [developer documentation](https://openrarity.gitbook.io/developers/) on how to integrate with OpenRarity.

# Setup and run tests locally

```
poetry install # install dependencies locally
poetry run pytest # run tests
```

# Library usage
Read [developer documentation](https://openrarity.gitbook.io/developers/) for advanced library usage


# Contributions guide and governance

OpenRarity is a community effort to improve rarity computation for NFTs (Non-Fungible Tokens). The core collaboration group consists of four primary contributors: [Curio](https://curio.tools), [icy.tools](https://icy.tools), [OpenSea](https://opensea.io) and [Proof](https://www.proof.xyz/)

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
- PyTest for unit tests

# License

Apache 2.0 , OpenSea, ICY, Curio, PROOF



[license-badge]: https://img.shields.io/github/license/ProjectOpenSea/open-rarity
[license-link]: https://github.com/ProjectOpenSea/open-rarity/blob/main/LICENSE
[ci-badge]: https://github.com/ProjectOpenSea/open-rarity/actions/workflows/tests.yaml/badge.svg
[ci-link]: https://github.com/ProjectOpenSea/open-rarity/actions/workflows/tests.yaml
[version-badge]: https://img.shields.io/github/v/release/ProjectOpenSea/open-rarity
[version-link]: https://github.com/ProjectOpenSea/open-rarity/releases?display_name=tag
