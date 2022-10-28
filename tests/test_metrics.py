# type: ignore
import pytest

from .references.metrics import FAILS, SUCCEEDS

_params = SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_init_metric_succeeds(params):
    assert params["metric"](**params["input"]) == params["_expected"]


_params = FAILS


@pytest.mark.parametrize("params", _params)
def test_init_metric_fails(params):
    with pytest.raises(params["_expected"]):
        params["metric"](**params["input"])
