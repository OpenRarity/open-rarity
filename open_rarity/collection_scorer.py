"""Pure collection scoring with optional creator settings."""

import math
import re
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

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
        ranked = RarityRanker.rank_collection(Collection(legacy))
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
    for token in tokens:
        values: dict[str, str] = {}
        invalid_date: set[str] = set()
        for trait in token.traits:
            name = trait.trait_type.strip()
            if trait.value is None or name == TRAIT_COUNT_ATTRIBUTE_NAME:
                continue
            if isinstance(trait.value, (int, float, Decimal)):
                value = format(Decimal(str(trait.value)), "f")
                if "." in value:
                    value = value.rstrip("0").rstrip(".")
                if Decimal(value) == 0:
                    value = "0"
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
        for name in names:
            selected_value = values.get(name)
            if name in numeric:
                number = (
                    None if name in invalid_dates[index] else _decimal(selected_value)
                )
                if number is not None:
                    count = len(numeric[name]) - bisect_left(numeric[name], number)
                    points -= _log2(count / total)
            else:
                count = frequencies[name][selected_value]
                points -= _log2(count / total)
                unique += selected_value is not None and count == 1
        token = tokens[index]
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
