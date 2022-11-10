from inspect import cleandoc

SUCCEEDS = [
    {
        "desc": cleandoc(
            """Non-fungible tokens with string traits."""
        ),
        "input": {
            "token_type": "non-fungible",
            "tokens": {
                1: {
                    "attributes": [
                        {"name": "weapon", "value": "axe"},
                        {"name": "Animated ", "value": "No "},
                    ]
                },
                2: {
                    "attributes": [
                        {"name": "weapon", "value": "kitana"},
                        {"name": "Animated ", "value": "No "},
                    ]
                }
            }
        },
        "_expected": {
            "token_supply": 2,
            "tokens": {
                1: {
                    'attributes': [
                        {
                            'name': 'animated',
                            'value': 'no',
                            'display_type': 'string',
                        },
                        {
                            'name': 'weapon',
                            'value': 'axe',
                            'display_type': 'string',
                        },
                        {
                            'name': 'openrarity.trait_count',
                            'value': 2,
                            'display_type': 'string',
                        }
                    ]
                },
                2: {
                    'attributes': [
                        {
                            'name': 'animated',
                            'value': 'no',
                            'display_type': 'string',
                        },
                        {
                            'name': 'weapon',
                            'value': 'kitana',
                            'display_type': 'string',
                        },
                        {
                            'name': 'openrarity.trait_count',
                            'value': 2,
                            'display_type': 'string',
                        }
                    ]
                }
            }
        }
    },
    {
        "desc": cleandoc(
            """Multiple values under same trait type."""
        ),
        "input": {
            "token_type": "non-fungible",
            "tokens": {
                1: {
                    "attributes": [
                        {"name": "weapon", "value": "axe"},
                        {"name": "weapon", "value": "kitana"},
                    ]
                }
            },
        },
        "_expected": {
            "token_supply": 1,
            "tokens": {
                1: {
                    "attributes": [
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
                            "value": 2,
                            "display_type": "string",
                        },
                    ]
                }
            }
        }
    },
    {
        "desc": cleandoc(
            """Duplicate traits."""
        ),
        "input": {
            "token_type": "non-fungible",
            "tokens": {
                1: {
                    "attributes": [
                        {"name": "weapon", "value": "axe"},
                        {"name": "weapon", "value": "axe"},
                    ]
                }
            }
        },
        "_expected": {
            "token_supply": 1,
            "tokens": {
                1: {
                    "attributes": [
                        {
                            "name": "weapon",
                            "value": "axe",
                            "display_type": "string",
                        },
                        {
                            "name": "openrarity.trait_count",
                            "value": 1,
                            "display_type": "string",
                        },
                    ]
                }
            }
        }
    },
    {
        "desc": cleandoc(
            """Semi-fungible tokens."""
        ),
        "input": {
            "token_type": "semi-fungible",
            "tokens": {
                1: {
                    "token_supply": 5,
                    "attributes": [
                        {"name": "medal", "value": "gold"}
                    ]
                },
                2: {
                    "token_supply": 10,
                    "attributes": [
                        {"name": "medal", "value": "silver"}
                    ]
                }
            }
        },
        "_expected": {
            "token_supply": {
                1: 5,
                2: 10,
            },
            "tokens": {
                1: {
                    'token_supply': 5,
                    'attributes': [
                        {
                            'name': 'medal',
                            'value': 'gold',
                            'display_type': 'string',
                        },
                        {
                            'name': 'openrarity.trait_count',
                            'value': 1,
                            'display_type': 'string',
                        }
                    ]
                },
                2: {
                    'token_supply': 10,
                    'attributes': [
                        {
                            'name': 'medal',
                            'value': 'silver',
                            'display_type': 'string',
                        },
                        {
                            'name': 'openrarity.trait_count',
                            'value': 1,
                            'display_type': 'string',
                        }
                    ]
                }
            }
        },
    },
    {
        "desc": cleandoc(
            """Numeric and date traits"""
        ),
        "input": {
            "token_type": "non-fungible",
            "tokens": {
                1: {
                    "attributes": [
                        {
                            "name": "level",
                            "value": 10,
                            "display_type": "number",
                        },
                        {
                            "name": "birthday",
                            "value": 1647519737,
                            "display_type": "date",
                        }
                    ]
                },
            }
        },
        "_expected": {
            "token_supply": 1,
            "tokens": {
                1: {
                    'attributes': [
                        {
                            'name': 'level',
                            'value': 10.0,
                            'display_type': 'number',
                        },
                        {
                            'name': 'birthday',
                            'value': 1647519737,
                            'display_type': 'date',
                        },
                        {
                            'name': 'openrarity.trait_count',
                            'value': 2,
                            'display_type': 'string',
                        }
                    ]
                }
            }
        }
    }
]


FAILS = [
    {
        "desc": cleandoc(
            """Semi-fungible missing token supply"""
        ),
        "input": {
            "token_type": "semi-fungible",
            "tokens": {
                1: {
                    "attributes": [
                        {"name": "medal", "value": "gold"}
                    ]
                }
            }
        },
        "_expected": {
            "expected_exception": ValueError, "match": "token_supply"
        },
    },
]
