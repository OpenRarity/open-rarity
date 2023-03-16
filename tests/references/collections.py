from inspect import cleandoc

SUCCEEDS = [
    {
        "desc": cleandoc(
            """
    Collection includes:
        - A `trait_type` key on one token.
        - Duplicate `name` with different `value`.
        - Missing `name` keys.
        - Missing `display_type` key.
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
                    {
                        "name": "shirt",
                        "value": "blue",
                        "display_type": "string",
                    },
                    {
                        "name": "shirt",
                        "value": "jacket",
                        "display_type": "string",
                    },
                    {"name": "pants", "value": "cargo shorts"},
                ]
            },
            2: {
                "attributes": [
                    {
                        "name": "hat",
                        "value": "cowboy",
                        "display_type": "string",
                    },
                    {"name": "shirt", "value": "tan", "display_type": "string"},
                    {
                        "name": "pants",
                        "value": "jeans",
                        "display_type": "string",
                    },
                ]
            },
            3: {
                "attributes": [
                    {
                        "name": "shirt",
                        "value": "blue",
                        "display_type": "string",
                    },
                    {
                        "name": "pants",
                        "value": "cargo shorts",
                        "display_type": "string",
                    },
                ]
            },
            4: {
                "attributes": [
                    {
                        "name": "shirt",
                        "value": "green",
                        "display_type": "string",
                    },
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
        "_expected": {
            2: 1,
            1: 2,
            4: 3,
            5: 3,
            3: 5,
        },
    },
    {
        "desc": cleandoc("""Collection with numeric traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "x", "value": 1, "display_type": "number"},
                    {"name": "y", "value": 1, "display_type": "number"},
                    {"name": "level", "value": 10, "display_type": "number"},
                ],
            },
            2: {
                "attributes": [
                    {"name": "x", "value": 1, "display_type": "number"},
                    {"name": "y", "value": 1, "display_type": "number"},
                    {"name": "level", "value": 9, "display_type": "number"},
                ],
            },
            3: {
                "attributes": [
                    {"name": "x", "value": 5, "display_type": "number"},
                    {"name": "y", "value": 5, "display_type": "number"},
                    {"name": "level", "value": 9, "display_type": "number"},
                ],
            },
        },
        "_expected": {
            3: 1,
            1: 2,
            2: 3,
        },
    },
    {
        "desc": cleandoc("""Collection with date traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {
                        "name": "start",
                        "value": 1640000000,
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": 1650000000,
                        "display_type": "date",
                    },
                ]
            },
            2: {
                "attributes": [
                    {
                        "name": "start",
                        "value": 1650000000,
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": 1660000000,
                        "display_type": "date",
                    },
                ]
            },
            3: {
                "attributes": [
                    {
                        "name": "start",
                        "value": 1640000000,
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": 1660000000,
                        "display_type": "date",
                    },
                ]
            },
        },
        "_expected": {
            1: 1,
            2: 1,
            3: 3,
        },
    },
    {
        "desc": cleandoc("""Collection with date traits in string format."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {
                        "name": "start",
                        "value": "2022-01-01T00:00:00",
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": "2022-02-01T00:00:00",
                        "display_type": "date",
                    },
                ]
            },
            2: {
                "attributes": [
                    {
                        "name": "start",
                        "value": "2022-02-01",
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": "2022-03-01",
                        "display_type": "date",
                    },
                ]
            },
            3: {
                "attributes": [
                    {
                        "name": "start",
                        "value": "2022-01-01",
                        "display_type": "date",
                    },
                    {
                        "name": "end",
                        "value": "2022-03-01T00:00:00",
                        "display_type": "date",
                    },
                ]
            },
        },
        "_expected": {
            1: 1,
            2: 1,
            3: 3,
        },
    },
    {
        "desc": cleandoc("""Item ranked higher for having unique trait count."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "color", "value": "red"},
                    {"name": "hat", "value": "baseball"},
                ]
            },
            2: {
                "attributes": [
                    {"name": "color", "value": "blue"},
                    {"name": "hat", "value": "baseball"},
                    {"name": "pants", "value": "jeans"},
                ]
            },
            3: {
                "attributes": [
                    {"name": "color", "value": "red"},
                    {"name": "hat", "value": "baseball"},
                    {"name": "pants", "value": "jeans"},
                ]
            },
        },
        "_expected": {
            1: 1,
            2: 2,
            3: 3,
        },
    },
    {
        "desc": cleandoc("""Semi-fungible collection sort by token_supply asc."""),
        "token_type": "semi-fungible",
        "tokens": {
            1: {
                "token_supply": 1,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "gold",
                        "display_type": "string",
                    },
                ],
            },
            2: {
                "token_supply": 10,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "silver",
                        "display_type": "string",
                    },
                ],
            },
            3: {
                "token_supply": 100,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "bronze",
                        "display_type": "string",
                    },
                ],
            },
        },
        "_expected": {
            1: 1,
            2: 2,
            3: 3,
        },
    },
    {
        "desc": cleandoc("""Semi-fungible collection all ranks same."""),
        "token_type": "semi-fungible",
        "tokens": {
            1: {
                "token_supply": 10,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "gold",
                        "display_type": "string",
                    },
                ],
            },
            2: {
                "token_supply": 10,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "silver",
                        "display_type": "string",
                    },
                ],
            },
            3: {
                "token_supply": 10,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "bronze",
                        "display_type": "string",
                    },
                ],
            },
        },
        "_expected": {
            1: 1,
            2: 1,
            3: 1,
        },
    },
    {
        "desc": cleandoc(
            """Semi-fungible collection first sort by trait rarity, then by
            token_supply asc.
            """
        ),
        "token_type": "semi-fungible",
        "tokens": {
            1: {
                "token_supply": 5,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "gold",
                        "display_type": "string",
                    },
                    {"name": "weight", "value": 100, "display_type": "number"},
                ],
            },
            2: {
                "token_supply": 5,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "silver",
                        "display_type": "string",
                    },
                    {"name": "weight", "value": 50, "display_type": "number"},
                ],
            },
            3: {
                "token_supply": 10,
                "attributes": [
                    {
                        "name": "medal",
                        "value": "bronze",
                        "display_type": "string",
                    },
                    {"name": "weight", "value": 50, "display_type": "number"},
                ],
            },
        },
        "_expected": {
            1: 1,
            2: 2,
            3: 3,
        },
    },
]


TEST_TOKENS_PARAMS = [
    {
        "desc": cleandoc("""Tokens with string traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "weapon", "value": "axe"},
                    {"name": "Animated ", "value": "No "},
                ]
            }
        },
        "_expected": {
            1: {
                "attributes": [
                    {
                        "name": "animated",
                        "value": "no",
                        "display_type": "string",
                    },
                    {
                        "name": "weapon",
                        "value": "axe",
                        "display_type": "string",
                    },
                    {
                        "name": "openrarity.trait_count",
                        "value": 2,
                        "display_type": "string",
                    },
                ]
            }
        },
    },
    {
        "desc": cleandoc("""Tokens with numeric traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "experience", "value": 2000, "display_type": "number"},
                    {"name": "Speed ", "value": 70.5, "display_type": "number"},
                ]
            }
        },
        "_expected": {
            1: {
                "attributes": [
                    {"name": "speed", "value": 70.5, "display_type": "number"},
                    {"name": "experience", "value": 2000.0, "display_type": "number"},
                    {
                        "name": "openrarity.trait_count",
                        "value": 2,
                        "display_type": "string",
                    },
                ]
            }
        },
    },
    {
        "desc": cleandoc("""Tokens with date traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "birthday", "value": 1647519737, "display_type": "date"},
                    {
                        "name": "Created At ",
                        "value": 1663221213,
                        "display_type": "date",
                    },
                ]
            }
        },
        "_expected": {
            1: {
                "attributes": [
                    {"name": "birthday", "value": 1647519737, "display_type": "date"},
                    {"name": "created at", "value": 1663221213, "display_type": "date"},
                    {
                        "name": "openrarity.trait_count",
                        "value": 2,
                        "display_type": "string",
                    },
                ]
            }
        },
    },
    {
        "desc": cleandoc("""Tokens with multiple values for same trait type."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "weapon", "value": "axe"},
                    {"name": "weapon", "value": "kitana"},
                    {"name": "Animated ", "value": "No "},
                ]
            }
        },
        "_expected": {
            1: {
                "attributes": [
                    {
                        "name": "animated",
                        "value": "no",
                        "display_type": "string",
                    },
                    {
                        "name": "weapon",
                        "value": "axe",
                        "display_type": "string",
                    },
                    {
                        "name": "weapon",
                        "value": "kitana",
                        "display_type": "string",
                    },
                    {
                        "name": "openrarity.trait_count",
                        "value": 3,
                        "display_type": "string",
                    },
                ]
            }
        },
    },
]


TEST_ATTRIBUTE_STATISTICS_PARAMS = [
    {
        "desc": cleandoc("""Tokens with string traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "weapon", "value": "axe"},
                    {"name": "animated", "value": "no"},
                    {"name": "eyewear", "value": "monocle"},
                ]
            },
            2: {
                "attributes": [
                    {"name": "weapon", "value": "kitana"},
                    {"name": "animated", "value": "no"},
                ]
            },
        },
        "_expected": {
            "string": [
                {
                    "name": "eyewear",
                    "value": "monocle",
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "weapon",
                    "value": "axe",
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "animated",
                    "value": "no",
                    "attribute.token_count": 2,
                    "attribute.supply": 2,
                    "metric.probability": 1.0,
                    "metric.information": -0.0,
                },
                {
                    "name": "openrarity.trait_count",
                    "value": 3,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "weapon",
                    "value": "kitana",
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "openrarity.trait_count",
                    "value": 2,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "eyewear",
                    "value": "openrarity.null_trait",
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
            ],
            "number": [],
            "date": [],
        },
    },
    {
        "desc": cleandoc("""Tokens with numeric traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "x", "value": 1, "display_type": "number"},
                    {"name": "y", "value": 2, "display_type": "number"},
                ]
            },
            2: {
                "attributes": [
                    {"name": "x", "value": 5, "display_type": "number"},
                    {"name": "y", "value": 10, "display_type": "number"},
                ]
            },
        },
        "_expected": {
            "string": [
                {
                    "name": "openrarity.trait_count",
                    "value": 2,
                    "attribute.token_count": 2,
                    "attribute.supply": 2,
                    "metric.probability": 1.0,
                    "metric.information": -0.0,
                }
            ],
            "number": [
                {
                    "name": "y",
                    "value": 2.0,
                    "bin": 2.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "y",
                    "value": 10.0,
                    "bin": 10.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "x",
                    "value": 1.0,
                    "bin": 1.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "x",
                    "value": 5.0,
                    "bin": 5.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
            ],
            "date": [],
        },
    },
    {
        "desc": cleandoc("""Tokens with date traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {
                        "name": "birthday",
                        "value": 1647519737,
                        "display_type": "date",
                    },
                ]
            },
            2: {
                "attributes": [
                    {
                        "name": "birthday",
                        "value": 1663221213,
                        "display_type": "date",
                    },
                ]
            },
        },
        "_expected": {
            "string": [
                {
                    "name": "openrarity.trait_count",
                    "value": 1,
                    "attribute.token_count": 2,
                    "attribute.supply": 2,
                    "metric.probability": 1.0,
                    "metric.information": -0.0,
                }
            ],
            "number": [],
            "date": [
                {
                    "name": "birthday",
                    "value": 1647519737,
                    "bin": 1647519737.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
                {
                    "name": "birthday",
                    "value": 1663221213,
                    "bin": 1663221213.0,
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.5,
                    "metric.information": 1.0,
                },
            ],
        },
    },
    {
        "desc": cleandoc("""Semi-fungible tokens."""),
        "token_type": "semi-fungible",
        "tokens": {
            1: {"token_supply": 1, "attributes": [{"name": "medal", "value": "gold"}]},
            2: {
                "token_supply": 9,
                "attributes": [{"name": "medal", "value": "silver"}],
            },
            3: {
                "token_supply": 90,
                "attributes": [{"name": "medal", "value": "bronze"}],
            },
        },
        "_expected": {
            "string": [
                {
                    "name": "medal",
                    "value": "gold",
                    "attribute.token_count": 1,
                    "attribute.supply": 1,
                    "metric.probability": 0.01,
                    "metric.information": 6.643856189774724,
                },
                {
                    "name": "openrarity.trait_count",
                    "value": 1,
                    "attribute.token_count": 3,
                    "attribute.supply": 100,
                    "metric.probability": 1.0,
                    "metric.information": -0.0,
                },
                {
                    "name": "medal",
                    "value": "silver",
                    "attribute.token_count": 1,
                    "attribute.supply": 9,
                    "metric.probability": 0.09,
                    "metric.information": 3.473931188332412,
                },
                {
                    "name": "medal",
                    "value": "bronze",
                    "attribute.token_count": 1,
                    "attribute.supply": 90,
                    "metric.probability": 0.9,
                    "metric.information": 0.15200309344504995,
                },
            ],
            "number": [],
            "date": [],
        },
    },
]


TEST_TOKEN_STATISTICS_PARAMS = [
    {
        "desc": cleandoc("""Tokens with string traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "weapon", "value": "axe"},
                ]
            }
        },
        "_expected": [
            {
                "token_id": 1,
                "name": "weapon",
                "value": "axe",
                "display_type": "string",
                "token.supply": 1,
                "attribute.token_count": 1,
                "attribute.supply": 1,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
            {
                "token_id": 1,
                "name": "openrarity.trait_count",
                "value": 1,
                "display_type": "string",
                "token.supply": 1,
                "attribute.token_count": 1,
                "attribute.supply": 1,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
        ],
    },
    {
        "desc": cleandoc("""Tokens with numeric traits."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [
                    {"name": "level", "value": 10, "display_type": "number"},
                ]
            }
        },
        "_expected": [
            {
                "token_id": 1,
                "name": "level",
                "value": 10.0,
                "display_type": "number",
                "token.supply": 1,
                "bin": 9.5,
                "attribute.token_count": 1,
                "attribute.supply": 1,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
            {
                "token_id": 1,
                "name": "openrarity.trait_count",
                "value": 1,
                "display_type": "string",
                "token.supply": 1,
                "attribute.token_count": 1,
                "attribute.supply": 1,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
        ],
    },
    {
        "desc": cleandoc("""Semi-fungible token."""),
        "token_type": "semi-fungible",
        "tokens": {
            1: {
                "token_supply": 10,
                "attributes": [
                    {"name": "weapon", "value": "axe"},
                ],
            }
        },
        "_expected": [
            {
                "token_id": 1,
                "name": "weapon",
                "value": "axe",
                "display_type": "string",
                "token.supply": 10,
                "attribute.token_count": 1,
                "attribute.supply": 10,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
            {
                "token_id": 1,
                "name": "openrarity.trait_count",
                "value": 1,
                "display_type": "string",
                "token.supply": 10,
                "attribute.token_count": 1,
                "attribute.supply": 10,
                "metric.probability": 1.0,
                "metric.information": -0.0,
            },
        ],
    },
]


TEST_CHECKSUM_PARAMS = [
    {
        "desc": cleandoc("""Checksum should be deterministic."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [{"name": "id", "value": "one", "display_type": "string"}]
            },
            2: {
                "attributes": [{"name": "id", "value": "two", "display_type": "string"}]
            },
            3: {
                "attributes": [
                    {"name": "id", "value": "three", "display_type": "string"}
                ]
            },
        },
    },
]


TEST_TOTAL_SUPPLY_PARAMS = [
    {
        "desc": cleandoc("""Non-fungible collection total supply."""),
        "token_type": "non-fungible",
        "tokens": {
            1: {
                "attributes": [{"name": "id", "value": "one", "display_type": "string"}]
            },
            2: {
                "attributes": [{"name": "id", "value": "two", "display_type": "string"}]
            },
            3: {
                "attributes": [
                    {"name": "id", "value": "three", "display_type": "string"}
                ]
            },
        },
        "_expected": 3,
    },
    {
        "desc": cleandoc("""Semi-fungible collection total supply."""),
        "token_type": "semi-fungible",
        "tokens": {
            1: {
                "token_supply": 1,
                "attributes": [
                    {"name": "id", "value": "one", "display_type": "string"}
                ],
            },
            2: {
                "token_supply": 10,
                "attributes": [
                    {"name": "id", "value": "two", "display_type": "string"}
                ],
            },
            3: {
                "token_supply": 100,
                "attributes": [
                    {"name": "id", "value": "three", "display_type": "string"}
                ],
            },
        },
        "_expected": 111,
    },
]
