from inspect import cleandoc

SUCCEEDS = [
    {
        "desc": cleandoc(
            """
    Collection includes:
        - A `trait_type` key on one token
        - Duplicate `name` with different `value`
        - Missing `name` keys
        - Missing `display_type` key

    """
        ),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {
                        "trait_type": "hat",
                        "value": "baseball",
                        "display_type": "string",
                    },
                    {"name": "shirt", "value": "blue", "display_type": "string"},
                    {"name": "shirt", "value": "jacket", "display_type": "string"},
                    {"name": "pants", "value": "cargo shorts"},
                ]
            },
            2: {
                "attributes": [
                    {"name": "hat", "value": "cowboy", "display_type": "string"},
                    {"name": "shirt", "value": "tan", "display_type": "string"},
                    {"name": "pants", "value": "jeans", "display_type": "string"},
                ]
            },
            3: {
                "attributes": [
                    {"name": "shirt", "value": "blue", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
            4: {
                "attributes": [
                    {"name": "shirt", "value": "green", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
            5: {
                "attributes": [
                    {"name": "shirt", "value": "red", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
        },
        "_expected": [
            {
                "token_id": 2,
                "probability": 0.0012800000000000005,
                "max_trait_ic": 2.321928094887362,
                "ic": 9.60964047443681,
                "unique_traits": 4,
                "rank": 1,
            },
            {
                "token_id": 1,
                "probability": 0.002560000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 8.60964047443681,
                "unique_traits": 3,
                "rank": 2,
            },
            {
                "token_id": 4,
                "probability": 0.04608000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 4.439715472994499,
                "unique_traits": 1,
                "rank": 3,
            },
            {
                "token_id": 5,
                "probability": 0.04608000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 4.439715472994499,
                "unique_traits": 1,
                "rank": 3,
            },
            {
                "token_id": 3,
                "probability": 0.09216000000000002,
                "max_trait_ic": 1.3219280948873622,
                "ic": 3.4397154729944988,
                "unique_traits": 0,
                "rank": 5,
            },
        ],
    },
    {
        "desc": cleandoc(
            """
    Collection includes:
        - A `trait_type` key on one token
        - Duplicate `name` with different `value`
        - Missing `name` keys
        - Missing `display_type` key

    """
        ),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {
                        "trait_type": "hat",
                        "value": "baseball",
                        "display_type": "string",
                    },
                    {"name": "shirt", "value": "blue", "display_type": "string"},
                    {"name": "shirt", "value": "jacket", "display_type": "string"},
                    {"name": "pants", "value": "cargo shorts"},
                ]
            },
            2: {
                "attributes": [
                    {"name": "hat", "value": "cowboy", "display_type": "string"},
                    {"name": "shirt", "value": "tan", "display_type": "string"},
                    {"name": "pants", "value": "jeans", "display_type": "string"},
                ]
            },
            3: {
                "attributes": [
                    {"name": "shirt", "value": "blue", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
            4: {
                "attributes": [
                    {"name": "shirt", "value": "green", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
            5: {
                "attributes": [
                    {"name": "shirt", "value": "red", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
        },
        "_expected": [
            {
                "token_id": 2,
                "probability": 0.0012800000000000005,
                "max_trait_ic": 2.321928094887362,
                "ic": 9.60964047443681,
                "unique_traits": 4,
                "rank": 1,
            },
            {
                "token_id": 1,
                "probability": 0.002560000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 8.60964047443681,
                "unique_traits": 3,
                "rank": 2,
            },
            {
                "token_id": 4,
                "probability": 0.04608000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 4.439715472994499,
                "unique_traits": 1,
                "rank": 3,
            },
            {
                "token_id": 5,
                "probability": 0.04608000000000001,
                "max_trait_ic": 2.321928094887362,
                "ic": 4.439715472994499,
                "unique_traits": 1,
                "rank": 3,
            },
            {
                "token_id": 3,
                "probability": 0.09216000000000002,
                "max_trait_ic": 1.3219280948873622,
                "ic": 3.4397154729944988,
                "unique_traits": 0,
                "rank": 5,
            },
        ],
    },
]
