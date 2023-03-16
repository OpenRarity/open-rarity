# type: ignore
import pytest

from .references.metrics import FAILS, SUCCEEDS

_params = SUCCEEDS


@pytest.mark.parametrize("params", _params)
def test_init_metric_succeeds(params):
    """Verify the result of `information_content()` and `count_traits()` methods by passing valid data."""
    assert params["metric"](**params["input"]) == params["_expected"]


_params = FAILS


@pytest.mark.parametrize("params", _params)
def test_init_metric_fails(params):
    """Verify the failure case of `information_content()` method by passing invalid data."""
    with pytest.raises(params["_expected"]):
        params["metric"](**params["input"])
