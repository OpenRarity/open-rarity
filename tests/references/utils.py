from inspect import cleandoc

MERGE_FAILS = [
    {
        "desc": cleandoc(
            """Valid left input and Invalid Right input to test merge() method failure case."""
        ),
        "token_type": "non-fungible",
        "input": {
            "left": [
                {"value1": 1, "value2": 1},
                {"value1": 1, "value2": 1},
                {"value1": 2, "value2": 1},
                {"value1": 2, "value2": 2},
                {"value1": 3, "value2": 2},
            ],
            "right": [
                {"value1": 1, "value2": 1, "value3": 1},
                {"value1": 1, "value2": 2, "value3": 2},
                {"value1": 2, "value2": 1, "value3": 3},
                {"value1": 3, "value2": 2, "value3": 4},
            ],
            "key": ("value1", "value2"),
        },
        "_expected": KeyError,
    }
]
MERGE_SUCCEEDS = [
    {
        "desc": cleandoc(
            """Valid Left and Right portions of the data to test merge() method."""
        ),
        "token_type": "non-fungible",
        "input": {
            "left": [
                {"value1": 1},
                {"value1": 1},
                {"value1": 2},
                {"value1": 2},
                {"value1": 3},
            ],
            "right": [
                {"value1": 1, "value2": 1},
                {"value1": 1, "value2": 2},
                {"value1": 2, "value2": 1},
                {"value1": 3, "value2": 3},
            ],
            "key": ("value1",),
        },
        "_expected": [
            {"value1": 1, "value2": 2},
            {"value1": 1, "value2": 2},
            {"value1": 2, "value2": 1},
            {"value1": 2, "value2": 1},
            {"value1": 3, "value2": 3},
        ],
    }
]
RANK_OVER_SUCCEEDS = [
    {
        "desc": cleandoc(
            """Valid Input data to test for rank_over() method."""
        ),
        "token_type": "non-fungible",
        "input": {
            "data": [
                {"value1": 1, "value2": 1},
                {"value1": 1, "value2": 1},
                {"value1": 1, "value2": 2},
                {"value1": 2, "value2": 1},
                {"value1": 2, "value2": 2},
                {"value1": 3, "value2": 2},
                {"value1": 3, "value2": 2},
            ],
            "key": ("value1", "value2"),
        },
        "_expected": [
            {"value1": 3, "value2": 2, "rank": 1},
            {"value1": 3, "value2": 2, "rank": 1},
            {"value1": 2, "value2": 2, "rank": 3},
            {"value1": 2, "value2": 1, "rank": 4},
            {"value1": 1, "value2": 2, "rank": 5},
            {"value1": 1, "value2": 1, "rank": 6},
            {"value1": 1, "value2": 1, "rank": 6},
        ],
    },
    {
        "desc": cleandoc(
            """Valid Input data to test for rank_over() method."""
        ),
        "token_type": "non-fungible",
        "input": {
            "data": [
                {"value1": 1},
                {"value1": 1},
                {"value1": 1},
                {"value1": 2},
                {"value1": 2},
                {"value1": 3},
                {"value1": 3},
            ],
            "key": ("value1",),
        },
        "_expected": [
            {"value1": 3, "rank": 1},
            {"value1": 3, "rank": 1},
            {"value1": 2, "rank": 3},
            {"value1": 2, "rank": 3},
            {"value1": 1, "rank": 5},
            {"value1": 1, "rank": 5},
            {"value1": 1, "rank": 5},
        ],
    },
]
