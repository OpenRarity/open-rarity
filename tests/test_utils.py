# type: ignore
import pytest

from openrarity.utils.data import merge, rank_over

from .references.utils import MERGE_FAILS, MERGE_SUCCEEDS, RANK_OVER_SUCCEEDS

_params = MERGE_FAILS


@pytest.mark.parametrize("params", _params)
def test_merge_fails(params):
    with pytest.raises(params["_expected"]):
        merge(**params["input"])


_params = MERGE_SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_merge(params):
    assert merge(**params["input"]) == params["_expected"]


_params = RANK_OVER_SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_rank_over(params):
    assert rank_over(**params["input"]) == params["_expected"]
