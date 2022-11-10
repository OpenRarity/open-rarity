# type: ignore
# import pytest
#
# from openrarity.token.token import NonFungibleTokenModel, SemiFungibleTokenModel
#
# from .references.tokens import FAILS, SUCCEEDS
#
# _params = SUCCEEDS
#
#
# @pytest.mark.parametrize("params", _params)
# def test_init_model_succeeds(params):
#
#     validated = params["model"](**params["input"]).dict()
#     if params["model"] in [NonFungibleTokenModel, SemiFungibleTokenModel]:
#         validated["attributes"] = sorted(
#             validated["attributes"], key=lambda attr: (attr["name"], attr["value"])
#         )
#     assert validated == params["_expected"]
#
#
# _params = FAILS
#
#
# @pytest.mark.parametrize("params", _params)
# def test_init_model_fails(params):
#     with pytest.raises(params["_expected"]):
#         params["model"](**params["input"])
