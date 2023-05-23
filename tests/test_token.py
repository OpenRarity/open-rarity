# type: ignore
import pytest

from openrarity.token.token import validate_tokens

from .references.tokens import FAILS, SUCCEEDS


@pytest.mark.parametrize("params", SUCCEEDS)
def test_validate_tokens_succeed(params):
    """Verify the result of `validate_tokens()` method by passing valid data."""
    token_supply, tokens = validate_tokens(**params["input"])
    assert token_supply == params["_expected"]["token_supply"]

    expected_tokens = params["_expected"]["tokens"]
    assert tokens.keys() == expected_tokens.keys()
    for token_id, token in tokens.items():
        expected_token = expected_tokens[token_id]
        if params["input"]["token_type"] == "semi-fungible":
            assert token["token_supply"] == expected_token["token_supply"]
        sorted_attrs = sorted(token["attributes"], key=lambda a: sorted(a.items()))
        expected_sorted_attrs = sorted(
            expected_token["attributes"], key=lambda a: sorted(a.items())
        )
        assert sorted_attrs == expected_sorted_attrs


@pytest.mark.parametrize("params", FAILS)
def test_validate_tokens_fail(params):
    """Verify the failure condition of `validate_tokens()` method by passing invalid data."""
    with pytest.raises(**params["_expected"]):
        validate_tokens(**params["input"])
