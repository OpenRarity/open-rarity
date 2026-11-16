import pytest

from open_rarity.creator_config import RarityConfig, parse_rarity_config


def test_parse_direct_and_contract_uri_rarity():
    rarity = {
        "trait_count": "exclude",
        "traits": [
            {"trait_type": " Level ", "mode": "exclude"},
            {"trait_type": "Level", "mode": "higher_is_rarer"},
            {"trait_type": "level", "mode": "exclude"},
        ],
    }
    expected = RarityConfig(
        excluded=frozenset({"level"}),
        higher_is_rarer=frozenset({"Level"}),
        trait_count="exclude",
    )
    assert parse_rarity_config(rarity) == expected
    assert parse_rarity_config({"rarity": rarity}) == expected
    assert expected.mode_for("Level") == "higher_is_rarer"
    assert expected.mode_for("level") == "exclude"
    assert expected.mode_for("meta_trait:trait_count") == "exclude"


def test_invalid_entries_do_not_hide_valid_settings():
    parsed = parse_rarity_config(
        {
            "trait_count": "unknown",
            "traits": [
                None,
                {"trait_type": 123, "mode": "exclude"},
                {"trait_type": " ", "mode": "exclude"},
                {"trait_type": "x" * 257, "mode": "exclude"},
                {"trait_type": "meta_trait:trait_count", "mode": "exclude"},
                {"trait_type": "Hat", "mode": "invalid"},
                {"trait_type": "Hat", "mode": "exclude"},
                {"trait_type": "Hat", "mode": None},
            ],
        }
    )
    assert parsed == RarityConfig(excluded=frozenset({"Hat"}))
    assert parsed.has_effect
    assert not parse_rarity_config({"rarity": []}).has_effect


def test_only_first_100_entries_are_used():
    traits = [
        {"trait_type": f"Trait {index}", "mode": "exclude"} for index in range(100)
    ]
    traits.append({"trait_type": "Too late", "mode": "exclude"})
    parsed = parse_rarity_config({"traits": traits})
    assert len(parsed.excluded) == 100
    assert "Too late" not in parsed.excluded


@pytest.mark.parametrize(
    "kwargs",
    [
        {"excluded": frozenset({"Hat"}), "higher_is_rarer": frozenset({"Hat"})},
        {"excluded": frozenset({"meta_trait:trait_count"})},
        {"excluded": frozenset({" Hat"})},
        {"trait_count": "unknown"},
    ],
)
def test_typed_config_rejects_conflicting_or_invalid_modes(kwargs):
    with pytest.raises(ValueError):
        RarityConfig(**kwargs)
