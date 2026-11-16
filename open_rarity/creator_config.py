"""Creator settings from the `rarity` object in contract-level metadata."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

RarityMode = Literal["exclude", "higher_is_rarer"]
TRAIT_COUNT_ATTRIBUTE_NAME = "meta_trait:trait_count"


@dataclass(frozen=True)
class RarityConfig:
    """Typed creator settings. Names are matched case-sensitively after trimming."""

    excluded: frozenset[str] = field(default_factory=frozenset)
    higher_is_rarer: frozenset[str] = field(default_factory=frozenset)
    trait_count: RarityMode | None = None

    def __post_init__(self) -> None:
        if self.excluded & self.higher_is_rarer:
            raise ValueError("A trait cannot have two rarity modes")
        if TRAIT_COUNT_ATTRIBUTE_NAME in self.excluded | self.higher_is_rarer:
            raise ValueError("Set the synthetic trait mode with trait_count")
        for name in self.excluded | self.higher_is_rarer:
            if not name or name != name.strip() or len(name) > 256:
                raise ValueError("Trait names must be trimmed and 1 to 256 characters")
        if self.trait_count not in (None, "exclude", "higher_is_rarer"):
            raise ValueError("Unknown trait_count rarity mode")

    @property
    def has_effect(self) -> bool:
        return bool(self.excluded or self.higher_is_rarer or self.trait_count)

    def mode_for(self, trait_type: str) -> RarityMode | None:
        if trait_type == TRAIT_COUNT_ATTRIBUTE_NAME:
            return self.trait_count
        if trait_type in self.excluded:
            return "exclude"
        if trait_type in self.higher_is_rarer:
            return "higher_is_rarer"
        return None


def parse_rarity_config(document_or_rarity: object) -> RarityConfig:
    """Skip malformed metadata entries while retaining every valid setting."""

    if not isinstance(document_or_rarity, Mapping):
        return RarityConfig()
    rarity = document_or_rarity.get("rarity", document_or_rarity)
    if not isinstance(rarity, Mapping):
        return RarityConfig()

    by_name: dict[str, RarityMode] = {}
    traits = rarity.get("traits")
    if isinstance(traits, list):
        for entry in traits[:100]:
            if not isinstance(entry, Mapping):
                continue
            name = entry.get("trait_type")
            mode = entry.get("mode")
            if not isinstance(name, str) or mode not in ("exclude", "higher_is_rarer"):
                continue
            name = name.strip()
            if not name or len(name) > 256 or name == TRAIT_COUNT_ATTRIBUTE_NAME:
                continue
            by_name[name] = mode

    trait_count = rarity.get("trait_count")
    if trait_count not in ("exclude", "higher_is_rarer"):
        trait_count = None
    return RarityConfig(
        excluded=frozenset(name for name, mode in by_name.items() if mode == "exclude"),
        higher_is_rarer=frozenset(
            name for name, mode in by_name.items() if mode == "higher_is_rarer"
        ),
        trait_count=trait_count,
    )
