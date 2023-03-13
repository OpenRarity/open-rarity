# type: ignore
import pytest

from openrarity.validators.string import clean_lower_string

_params = [
    {"input": "   Hello", "_expected": "hello"},
    {"input": None, "_expected": None},
]


@pytest.mark.parametrize("params", _params)
def test_clean_lower_string_succeeds(params):
    """A method to test for clean_lower_string operation success."""
    assert clean_lower_string(params["input"]) == params["_expected"]


_params = [
    {"input": 1, "_expected": AttributeError},
]


@pytest.mark.parametrize("params", _params)
def test_clean_lower_string_fails(params):
    """A method to test for clean_lower_string operation failure."""
    with pytest.raises(params["_expected"]):
        clean_lower_string(params["input"])
