import pytest
from unittest.mock import Mock

from open_rarity.resolver.opensea_api_helpers import (
    OpenSeaClient,
    get_collection_from_opensea,
)


from open_rarity.resolver.opensea_api_helpers import (
    opensea_traits_to_token_metadata,
)


def test_untyped_numeric_traits_do_not_enter_string_normalization() -> None:
    metadata = opensea_traits_to_token_metadata(
        [
            {"trait_type": "Level", "value": 7, "display_type": None},
            {"trait_type": "Power", "value": 1.5},
            {"trait_type": "Hat", "value": "Cap", "display_type": None},
            {"trait_type": "Empty", "value": None, "display_type": None},
        ]
    )

    assert metadata.numeric_attributes["level"].value == 7
    assert metadata.numeric_attributes["power"].value == 1.5
    assert metadata.string_attributes["hat"].value == "cap"
    assert "empty" not in metadata.string_attributes
    assert "empty" not in metadata.numeric_attributes


def response(data, status=200, headers=None):
    result = Mock(status_code=status, headers=headers or {})
    result.json.return_value = data
    if status >= 400:
        import requests

        result.raise_for_status.side_effect = requests.HTTPError(str(status))
    return result


def nft(identifier, traits=None):
    return {
        "identifier": identifier,
        "contract": "0xabc",
        "collection": "sample",
        "token_standard": "erc721",
        "traits": traits or [],
    }


def test_v2_cursor_sparse_ids_empty_traits_and_actual_supply(mocker):
    get = mocker.patch(
        "requests.Session.get",
        side_effect=[
            response(
                {
                    "name": "Sample",
                    "total_supply": 99999,
                    "contracts": [{"chain": "arbitrum", "address": "0xabc"}],
                }
            ),
            response({"nfts": [nft("7")], "next": "cursor"}),
            response({"nfts": [nft("9007199254740993")], "next": None}),
        ],
    )
    collection = get_collection_from_opensea("sample", chain="arbitrum")
    assert collection.token_total_supply == 2
    assert [t.token_identifier.token_id for t in collection.tokens] == [
        7,
        9007199254740993,
    ]
    assert get.call_args_list[2].kwargs["params"]["next"] == "cursor"
    assert all(c.kwargs["timeout"] == 30 for c in get.call_args_list)
    assert all(c.kwargs["allow_redirects"] is False for c in get.call_args_list)


@pytest.mark.parametrize(
    "pages",
    [
        [{"nfts": [], "next": "same"}, {"nfts": [], "next": "same"}],
        [{"nfts": [nft("1")], "next": "next"}, {"nfts": [nft("1")]}],
        [{"wrong": []}],
    ],
)
def test_incomplete_or_duplicate_snapshot_fails(pages):
    session = Mock()
    session.get.side_effect = [response(p) for p in pages]
    with pytest.raises(ValueError):
        list(OpenSeaClient(session=session).iter_nfts("sample"))


def test_retry_and_runtime_key(mocker, monkeypatch):
    monkeypatch.setenv("OPENSEA_API_KEY", "test-only")
    session = Mock()
    session.get.side_effect = [
        response({}, 429, {"Retry-After": "1"}),
        response({"name": "ok"}),
    ]
    sleep = mocker.patch("open_rarity.resolver.opensea_api_helpers.time.sleep")
    assert (
        OpenSeaClient(session=session, testnet=True).collection("a/b")["name"] == "ok"
    )
    sleep.assert_called_once_with(1)
    assert (
        session.get.call_args.args[0]
        == "https://testnets-api.opensea.io/api/v2/collections/a%2Fb"
    )
    assert session.get.call_args.kwargs["headers"]["X-API-KEY"] == "test-only"


def test_permanent_error_does_not_return_partial_collection(mocker):
    import requests

    session = Mock()
    session.get.side_effect = [
        response({"nfts": [nft("7")], "next": "more"}),
        response({}, 403),
    ]
    sleep = mocker.patch("open_rarity.resolver.opensea_api_helpers.time.sleep")
    with pytest.raises(requests.HTTPError):
        list(OpenSeaClient(session=session).iter_nfts("sample"))
    sleep.assert_not_called()
