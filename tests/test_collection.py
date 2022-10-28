# type: ignore
import pytest

from openrarity import TokenCollection

from .references.collections import SUCCEEDS

_params = SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_rank_collection_succeeds(params):
    tc = TokenCollection(params["token_type"], params["tokens"])
    ranks = tc.rank_collection(return_ranks=True)
    assert ranks == params["_expected"]
