"""Pure collection scoring with optional creator settings."""

import math
import re
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from open_rarity.collection_input import CollectionInput
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
    if value is None or not re.fullmatch(
        r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value
    ):
        return None
    try:
        number = Decimal(value)
        return number if number.is_finite() else None
    except InvalidOperation:
        return None


def score_collection(
    collection: CollectionInput, config: RarityConfig | None = None
) -> list[TokenRarityResult]:
    """Rank a complete collection without changing its source metadata."""
    tokens = collection.tokens
    if len({t.token_id for t in tokens}) != len(tokens):
        raise ValueError("Duplicate token ID")
    if not tokens:
        return []
    for token in tokens:
        if not isinstance(token.token_id, str) or not token.token_id:
            raise ValueError("Token IDs must be nonempty strings")
        if token.token_id_kind not in ("evm", "raw"):
            raise ValueError("Unknown token ID kind")
        if token.token_id_kind == "evm" and not re.fullmatch(r"[0-9]+", token.token_id):
            raise ValueError("EVM token IDs must contain unsigned decimal digits")
    if config is None or not config.has_effect:
        legacy = []
        for token in tokens:
            attributes = {trait.trait_type: trait.value for trait in token.traits}
            legacy.append(
                Token.from_erc721("0x0", int(token.token_id), attributes)
                if token.token_id_kind == "evm"
                else Token.from_metaplex_non_fungible(token.token_id, attributes)
            )
        original_ids = {id(t): source.token_id for t, source in zip(legacy, tokens)}
        return [
            TokenRarityResult(
                original_ids[id(result.token)],
                result.score,
                result.rank or 1,
                result.token_features.unique_attribute_count,
            )
            for result in RarityRanker.rank_collection(Collection(legacy))
        ]

    selected: list[dict[str, str]] = []
    for token in tokens:
        values: dict[str, str] = {}
        for trait in token.traits:
            name = trait.trait_type.strip()
            if trait.value is None or name == TRAIT_COUNT_ATTRIBUTE_NAME:
                continue
            value = str(trait.value).strip()
            if not value or value.lower() == "none":
                continue
            if name not in values or value < values[name]:
                values[name] = value
        count = sum(config.mode_for(name) is None for name in values)
        if config.trait_count != "exclude":
            values[TRAIT_COUNT_ATTRIBUTE_NAME] = str(count)
        selected.append(
            {k: v for k, v in values.items() if config.mode_for(k) != "exclude"}
        )

    names = sorted({name for values in selected for name in values})
    total = len(tokens)
    frequencies = {name: Counter(v.get(name) for v in selected) for name in names}
    entropy = (
        -sum(
            (count / total) * math.log2(count / total)
            for counts in frequencies.values()
            for count in counts.values()
        )
        or 1.0
    )
    numeric = {
        name: sorted(
            number
            for values in selected
            if (number := _decimal(values.get(name))) is not None
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
                number = _decimal(selected_value)
                if number is not None:
                    count = len(numeric[name]) - bisect_left(numeric[name], number)
                    points -= math.log2(count / total)
            else:
                count = frequencies[name][selected_value]
                points -= math.log2(count / total)
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
        rank = results[-1].rank if results and results[-1].score == score else index + 1
        results.append(TokenRarityResult(token_id, score, rank, unique))
    return results
