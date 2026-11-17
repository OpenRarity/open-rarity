"""Opt-in read-only smoke check; never logs request headers or credentials."""

from open_rarity.resolver.opensea_api_helpers import OpenSeaClient


def main() -> None:
    with OpenSeaClient() as client:
        collection = client.collection("doodles-official")
        first = next(client.iter_nfts("doodles-official", page_size=1))
        contracts = collection["contracts"]
        chain = next(
            c["chain"]
            for c in contracts
            if c["address"].lower() == first["contract"].lower()
        )
        detail = client.nft(chain, first["contract"], first["identifier"])
        assert detail["identifier"] == first["identifier"]
        assert isinstance(first["traits"], list)
        print(
            "PASS: collection, NFT page, and NFT detail returned HTTP 200 with matching identifiers"
        )


if __name__ == "__main__":
    main()
