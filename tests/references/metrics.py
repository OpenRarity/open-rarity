from inspect import cleandoc

from openrarity.metrics.ic import information_content
from openrarity.metrics.trait_count import count_traits

SUCCEEDS = [
    {
        "desc": cleandoc(
            """Valid Input Data for init metrics"""
        ),
        "metric": information_content,
        "input": {
            "counts": [
                {
                    "name": "name",
                    "value": "value",
                    "attribute.token_count": 3,
                    "attribute.supply": 3,
                }
            ],
            "total": 6,
        },
        "_expected": [
            {
                "name": "name",
                "value": "value",
                "attribute.token_count": 3,
                "attribute.supply": 3,
                "metric.probability": 0.5,
                "metric.information": 1.0,
            }
        ],
    },
    {
        "desc": cleandoc(
            """
        """
        ),
        "metric": count_traits,
        "input": {
            "attributes": [
                {"name": "shirt", "value": "jacket", "display_type": "string"},
                {
                    "name": "pants",
                    "value": "cargo shorts",
                    "display_type": "string",
                },
                {"name": "shirt", "value": "blue", "display_type": "string"},
                {"name": "hat", "value": "baseball", "display_type": "string"},
            ]
        },
        "_expected": [
            {"name": "shirt", "value": "jacket", "display_type": "string"},
            {
                "name": "pants",
                "value": "cargo shorts",
                "display_type": "string",
            },
            {"name": "shirt", "value": "blue", "display_type": "string"},
            {"name": "hat", "value": "baseball", "display_type": "string"},
            {
                "name": "openrarity.trait_count",
                "value": 4,
                "display_type": "string",
            },
        ],
    },
]

FAILS = [
    {
        "desc": cleandoc(
            """Invalid input data for init metrics"""
        ),
        "metric": information_content,
        "input": {
            "counts": [
                {
                    "name": "name",
                    "value": "value",
                }
            ],
            "total": 6,
        },
        "_expected": KeyError,
    },
]
