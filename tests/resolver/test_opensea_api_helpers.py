from open_rarity.resolver.opensea_api_helpers import (
    opensea_traits_to_token_metadata,
)


def test_untyped_numeric_traits_do_not_enter_string_normalization() -> None:
    metadata = opensea_traits_to_token_metadata(
        [
            {"trait_type": "Level", "value": 7, "display_type": None},
            {"trait_type": "Power", "value": 1.5},
            {"trait_type": "Hat", "value": "Cap", "display_type": None},
            {"trait_type": "Empty", "value": None, "display_type": None},
        ]
    )

    assert metadata.numeric_attributes["level"].value == 7
    assert metadata.numeric_attributes["power"].value == 1.5
    assert metadata.string_attributes["hat"].value == "cap"
    assert "empty" not in metadata.string_attributes
    assert "empty" not in metadata.numeric_attributes
