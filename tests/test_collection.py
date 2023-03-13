# type: ignore
import copy

import pytest

from openrarity import TokenCollection

from .references.collections import (
    SUCCEEDS,
    TEST_ATTRIBUTE_STATISTICS_PARAMS,
    TEST_CHECKSUM_PARAMS,
    TEST_TOKEN_STATISTICS_PARAMS,
    TEST_TOKENS_PARAMS,
    TEST_TOTAL_SUPPLY_PARAMS,
)

_params = SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_rank_collection_succeeds(params):
    """A method to test whether we receive correct ranks or not."""
    tc = TokenCollection(params["token_type"], params["tokens"])
    ranks = tc.rank_collection(return_ranks=True)
    tid_to_rank = {token["token_id"]: token["rank"] for token in ranks}
    assert tid_to_rank == params["_expected"]


@pytest.mark.parametrize("params", TEST_TOKENS_PARAMS)
def test_tokens(params):
    """A method to test whether we received required token params are not"""
    tc = TokenCollection(params["token_type"], params["tokens"])
    expected_tokens = params["_expected"]
    assert tc.tokens.keys() == expected_tokens.keys()
    for token_id, token in tc.tokens.items():
        expected_token = expected_tokens[token_id]
        sorted_attr = sorted(token["attributes"], key=lambda a: (a["name"], a["value"]))
        expected_sorted_attr = sorted(
            expected_token["attributes"], key=lambda a: (a["name"], a["value"])
        )
        assert sorted_attr == expected_sorted_attr


@pytest.mark.parametrize("params", TEST_ATTRIBUTE_STATISTICS_PARAMS)
def test_attribute_statistics(params):
    """A method to test attribute statistics."""
    tc = TokenCollection(params["token_type"], params["tokens"])
    tc.rank_collection()
    for key, attr_stat in tc.attribute_statistics.items():
        expected_attr_stat = params["_expected"][key]
        sorted_attr_stat = sorted(attr_stat, key=lambda a: sorted(a.items()))
        expected_sorted_attr_stat = sorted(
            expected_attr_stat, key=lambda a: sorted(a.items())
        )
        assert sorted_attr_stat == expected_sorted_attr_stat


@pytest.mark.parametrize("params", TEST_TOKEN_STATISTICS_PARAMS)
def test_token_statistics(params):
    """A method to test for Token statistics."""
    tc = TokenCollection(params["token_type"], params["tokens"])
    tc.rank_collection()
    sorted_stats = sorted(tc.token_statistics, key=lambda s: sorted(s.items()))
    expected_sorted_stats = sorted(params["_expected"], key=lambda s: sorted(s.items()))
    assert sorted_stats == expected_sorted_stats


@pytest.mark.parametrize("params", TEST_CHECKSUM_PARAMS)
def test_checksum(params):
    """A method to test for collection checksum."""
    def _compute_checksum():
        tc = TokenCollection(
            copy.deepcopy(params["token_type"]), copy.deepcopy(params["tokens"])
        )
        tc.rank_collection()
        return tc.checksum

    first_checksum = _compute_checksum()
    for _ in range(10):
        assert _compute_checksum() == first_checksum


@pytest.mark.parametrize("params", TEST_TOTAL_SUPPLY_PARAMS)
def test_total_supply(params):
    """A method to test for total supply value."""
    tc = TokenCollection(params["token_type"], params["tokens"])
    tc.rank_collection()
    assert tc.total_supply == params["_expected"]
