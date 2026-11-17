"""Pure collection scoring with optional creator settings."""

import math
import re
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

import numpy as np

from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)

from open_rarity.collection_input import CollectionInput, TokenInput
from open_rarity.creator_config import RarityConfig, TRAIT_COUNT_ATTRIBUTE_NAME
from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.rarity_ranker import RarityRanker


@dataclass(frozen=True)
class TokenRarityResult:
    token_id: str
    score: float
    rank: int
    unique_trait_count: int


@dataclass(frozen=True)
class SourceTrait:
    trait_type: str
    value: str | None
    value_kind: Literal["string", "number", "null"]
    display_type: str | None


@dataclass(frozen=True)
class TraitExplanation:
    trait_type: str
    value: str | None
    mode: Literal["frequency", "higher_is_rarer", "exclude"]
    count: int | None
    probability: float | None
    information: float
    contribution: float
    unique: bool


@dataclass(frozen=True)
class ExplainedToken:
    result: TokenRarityResult
    normalization: float
    traits: list[TraitExplanation]
    source_traits: list[SourceTrait]


def explain_collection(
    collection: CollectionInput, config: RarityConfig | None = None
) -> list[ExplainedToken]:
    """Score once and expose selected values and per-trait contributions."""
    details: dict[str, tuple[float, list[TraitExplanation]]] = {}
    results = _score_collection(collection, config, details)
    sources = {token.token_id: token for token in collection.tokens}
    return [
        ExplainedToken(
            result,
            *details[result.token_id],
            [
                SourceTrait(
                    t.trait_type,
                    None
                    if t.value is None
                    else t.value
                    if isinstance(t.value, str)
                    else _number_text(t.value),
                    "null"
                    if t.value is None
                    else "string"
                    if isinstance(t.value, str)
                    else "number",
                    t.display_type,
                )
                for t in sources[result.token_id].traits
            ],
        )
        for result in results
    ]


def _number_text(value: int | float | Decimal) -> str:
    text = format(Decimal(str(value)), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if Decimal(text) == 0 else text


def _decimal(value: str | None) -> Decimal | None:
    if (
        value is None
        or len(value) > 1024
        or not re.fullmatch(
            r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value
        )
    ):
        return None
    try:
        number = Decimal(value)
        return (
            number
            if number.is_finite() and abs(int(number.as_tuple().exponent)) <= 10000
            else None
        )
    except InvalidOperation:
        return None


def score_collection(
    collection: CollectionInput, config: RarityConfig | None = None
) -> list[TokenRarityResult]:
    """Rank a complete collection without changing its source metadata."""
    return _score_collection(collection, config)


def _score_collection(
    collection: CollectionInput,
    config: RarityConfig | None = None,
    details: dict[str, tuple[float, list[TraitExplanation]]] | None = None,
) -> list[TokenRarityResult]:
    tokens = collection.tokens
    if not tokens:
        return []
    for token in tokens:
        if not isinstance(token.token_id, str) or not token.token_id:
            raise ValueError("Token IDs must be nonempty strings")
        if token.token_id_kind not in ("evm", "raw"):
            raise ValueError("Unknown token ID kind")
        if token.token_id_kind == "evm" and not re.fullmatch(r"[0-9]+", token.token_id):
            raise ValueError("EVM token IDs must contain unsigned decimal digits")
    if len({t.token_id for t in tokens}) != len(tokens):
        raise ValueError("Duplicate token ID")
    for token in tokens:
        for trait in token.traits:
            if not isinstance(trait.trait_type, str):
                raise ValueError("Trait names must be strings")
            if trait.display_type is not None and not isinstance(
                trait.display_type, str
            ):
                raise ValueError("Invalid display_type")
            value = trait.value
            if isinstance(value, bool) or not isinstance(
                value, (str, int, float, Decimal, type(None))
            ):
                raise ValueError("Invalid trait value")
            if (
                isinstance(value, (int, float, Decimal))
                and _decimal(str(value)) is None
            ):
                raise ValueError("Invalid or oversized decimal")
            if (
                isinstance(value, float)
                and value.is_integer()
                and abs(value) > 2**53 - 1
            ):
                raise ValueError(
                    "Use parse_collection_json for exact large numeric values"
                )
    configured = config is not None and config.has_effect
    config = config or RarityConfig()
    if not configured and all(
        isinstance(t.value, str) for token in tokens for t in token.traits
    ):
        legacy = []
        for token in tokens:
            attributes = {trait.trait_type: trait.value for trait in token.traits}
            legacy.append(
                Token.from_erc721("0x0", int(token.token_id), attributes)
                if token.token_id_kind == "evm"
                else Token.from_metaplex_non_fungible(token.token_id, attributes)
            )
        originals = {id(t): source for t, source in zip(legacy, tokens)}
        legacy_collection = Collection(legacy)
        ranked = RarityRanker.rank_collection(legacy_collection)
        if details is not None:
            normalization = (
                float(
                    InformationContentScoringHandler()._get_collection_entropy(
                        legacy_collection
                    )
                )
                or 1.0
            )
            legacy_frequencies = legacy_collection.attributes_frequency_counts
            missing = {
                name: len(tokens) - sum(legacy_counts.values())
                for name, legacy_counts in legacy_frequencies.items()
            }
            for token, source in zip(legacy, tokens):
                traits = []
                for name in sorted(legacy_frequencies):
                    attribute = token.metadata.string_attributes.get(name)
                    value = attribute.value if attribute else None
                    legacy_count = (
                        legacy_frequencies[name][value]
                        if value is not None
                        else missing[name]
                    )
                    information = float(
                        -np.log2(np.reciprocal(float(len(tokens) / legacy_count)))
                    )
                    traits.append(
                        TraitExplanation(
                            name,
                            value,
                            "frequency",
                            legacy_count,
                            legacy_count / len(tokens),
                            information,
                            information / normalization,
                            value is not None and legacy_count == 1,
                        )
                    )
                details[source.token_id] = (normalization, traits)
        ranked.sort(
            key=lambda r: (
                -r.token_features.unique_attribute_count,
                -r.score,
                _id_key(originals[id(r.token)]),
            )
        )
        return [
            TokenRarityResult(
                originals[id(r.token)].token_id,
                r.score,
                r.rank or 1,
                r.token_features.unique_attribute_count,
            )
            for r in ranked
        ]

    selected: list[dict[str, str]] = []
    invalid_dates: list[set[str]] = []
    excluded_values: list[dict[str, str]] = []
    for token in tokens:
        values: dict[str, str] = {}
        invalid_date: set[str] = set()
        for trait in token.traits:
            name = trait.trait_type.strip()
            if trait.value is None or name == TRAIT_COUNT_ATTRIBUTE_NAME:
                continue
            if isinstance(trait.value, (int, float, Decimal)):
                value = _number_text(trait.value)
            else:
                value = trait.value.strip()
            if configured:
                if not value or value.lower() == "none":
                    continue
            else:
                name, value = name.lower(), value.lower()
            if not configured or name not in values or value < values[name]:
                values[name] = value
                invalid_date.discard(name)
                if trait.display_type == "date":
                    date = _decimal(value)
                    if date is None or date != date.to_integral_value():
                        invalid_date.add(name)
        count = sum(
            config.mode_for(name) is None and value.lower() not in ("", "none")
            for name, value in values.items()
        )
        if config.trait_count != "exclude":
            values[TRAIT_COUNT_ATTRIBUTE_NAME] = str(count)
        if details is not None:
            excluded_values.append(
                {k: v for k, v in values.items() if config.mode_for(k) == "exclude"}
            )
        invalid_dates.append(invalid_date)
        selected.append(
            {k: v for k, v in values.items() if config.mode_for(k) != "exclude"}
        )

    names = sorted({name for values in selected for name in values})
    total = len(tokens)
    frequencies = {name: Counter(v.get(name) for v in selected) for name in names}
    entropy = 0.0
    for counts in frequencies.values():
        for count in counts.values():
            probability = count / total
            entropy -= probability * _log2(probability)
    entropy = entropy or 1.0
    numeric = {
        name: sorted(
            number
            for i, values in enumerate(selected)
            if name not in invalid_dates[i]
            and (number := _decimal(values.get(name))) is not None
        )
        for name in names
        if config.mode_for(name) == "higher_is_rarer"
    }
    scored = []
    for index, values in enumerate(selected):
        points = 0.0
        unique = 0
        explanations = []
        for name in names:
            match_count: int | None = None
            information = 0.0
            is_unique = False
            selected_value = values.get(name)
            if name in numeric:
                number = (
                    None if name in invalid_dates[index] else _decimal(selected_value)
                )
                if number is not None:
                    match_count = len(numeric[name]) - bisect_left(
                        numeric[name], number
                    )
                    information = -_log2(match_count / total)
                    points += information
            else:
                match_count = frequencies[name][selected_value]
                information = -_log2(match_count / total)
                points += information
                is_unique = selected_value is not None and match_count == 1
                unique += is_unique
            if details is not None:
                explanations.append(
                    TraitExplanation(
                        name,
                        selected_value,
                        "higher_is_rarer" if name in numeric else "frequency",
                        match_count,
                        match_count / total if match_count is not None else None,
                        information,
                        information / entropy,
                        is_unique,
                    )
                )
        token = tokens[index]
        if details is not None:
            for name in sorted(
                config.excluded
                | (
                    {TRAIT_COUNT_ATTRIBUTE_NAME}
                    if config.trait_count == "exclude"
                    else set()
                )
            ):
                explanations.append(
                    TraitExplanation(
                        name,
                        excluded_values[index].get(name),
                        "exclude",
                        None,
                        None,
                        0.0,
                        0.0,
                        False,
                    )
                )
            explanations.sort(key=lambda t: t.trait_type)
            details[token.token_id] = (entropy, explanations)
        key = (
            (0, int(token.token_id), token.token_id)
            if token.token_id_kind == "evm"
            else (1, 0, token.token_id)
        )
        scored.append((unique, points / entropy, key, token.token_id))
    scored.sort(key=lambda item: (-item[0], -item[1], item[2]))
    results: list[TokenRarityResult] = []
    for index, (unique, score, _, token_id) in enumerate(scored):
        rank = (
            results[-1].rank
            if results
            and (
                results[-1].score == score
                if configured
                else math.isclose(results[-1].score, score, rel_tol=1e-9, abs_tol=0)
            )
            else index + 1
        )
        results.append(TokenRarityResult(token_id, score, rank, unique))
    return results


def _id_key(token: TokenInput):
    return (
        (0, int(token.token_id), token.token_id)
        if token.token_id_kind == "evm"
        else (1, 0, token.token_id)
    )


def _log2(value: float) -> float:
    """Match TypeScript binary64 operations instead of platform libm rounding."""
    exponent = 0
    while value < 1:
        value *= 2
        exponent -= 1
    while value >= 2:
        value /= 2
        exponent += 1
    z = (value - 1) / (value + 1)
    square = z * z
    term = total = z
    for denominator in range(3, 61, 2):
        term *= square
        total += term / denominator
    return exponent + (2 * total) / 0.6931471805599453
