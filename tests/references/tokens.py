# from inspect import cleandoc

# from openrarity.token.token import (
#     MetadataAttributeModel,
#     NonFungibleTokenModel,
#     SemiFungibleTokenModel,
# )

# # type: ignore
# SUCCEEDS = [
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": NonFungibleTokenModel,
#         "input": {
#             "attributes": [
#                 {"trait_type": "hat", "value": "baseball", "display_type": "string"},
#                 {"name": "shirt", "value": "blue", "display_type": "string"},
#                 {"name": "shirt", "value": "jacket", "display_type": "string"},
#                 {"name": "pants", "value": "cargo shorts"},
#             ]
#         },
#         "_expected": {
#             "attributes": sorted(
#                 [
#                     {"name": "shirt", "value": "jacket", "display_type": "string"},
#                     {
#                         "name": "pants",
#                         "value": "cargo shorts",
#                         "display_type": "string",
#                     },
#                     {"name": "shirt", "value": "blue", "display_type": "string"},
#                     {"name": "hat", "value": "baseball", "display_type": "string"},
#                     {
#                         "name": "openrarity.trait_count",
#                         "value": 4,
#                         "display_type": "string",
#                     },
#                 ],
#                 key=lambda attr: (attr["name"], attr["value"]),
#             )
#         },
#     },
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": SemiFungibleTokenModel,
#         "input": {
#             "token_supply": 10000,
#             "attributes": [
#                 {"trait_type": "hat", "value": "baseball", "display_type": "string"},
#                 {"name": "shirt", "value": "blue", "display_type": "string"},
#                 {"name": "shirt", "value": "jacket", "display_type": "string"},
#                 {"name": "pants", "value": "cargo shorts"},
#             ],
#         },
#         "_expected": {
#             "token_supply": 10000,
#             "attributes": sorted(
#                 [
#                     {"name": "shirt", "value": "jacket", "display_type": "string"},
#                     {
#                         "name": "pants",
#                         "value": "cargo shorts",
#                         "display_type": "string",
#                     },
#                     {"name": "shirt", "value": "blue", "display_type": "string"},
#                     {"name": "hat", "value": "baseball", "display_type": "string"},
#                     {
#                         "name": "openrarity.trait_count",
#                         "value": 4,
#                         "display_type": "string",
#                     },
#                 ],
#                 key=lambda attr: (attr["name"], attr["value"]),
#             ),
#         },
#     },
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": MetadataAttributeModel,
#         "input": {"trait_type": "hat", "value": "baseball", "display_type": "string"},
#         "_expected": {
#             "name": "hat",
#             "value": "baseball",
#             "display_type": "string",
#         },
#     },
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": MetadataAttributeModel,
#         "input": {"trait_type": "animal", "value": "cat", "display_type": "Meow"},
#         "_expected": {
#             "name": "animal",
#             "value": "cat",
#             "display_type": "string",
#         },
#     },
# ]
# # type: ignore
# FAILS = [  # type: ignore
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": NonFungibleTokenModel,
#         "input": {},
#         "_expected": KeyError,
#     },
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": SemiFungibleTokenModel,
#         "input": {
#             "attributes": [
#                 {"trait_type": "hat", "value": "baseball", "display_type": "string"},
#             ],
#         },
#         "_expected": ValidationError,
#     },
#     {
#         "desc": cleandoc(
#             """
#             """
#         ),
#         "model": MetadataAttributeModel,
#         "input": {"trait_name": "hat", "value": "baseball", "display_type": "string"},
#         "_expected": ValidationError,
#     },
# ]
