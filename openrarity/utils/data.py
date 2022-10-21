from typing import Hashable


def merge(left: list[dict], right: list[dict], key: tuple[Hashable]) -> list[dict]:
    right = {tuple((row[k] for k in key)): row for row in right}
    return [{**lrow, **right[tuple((lrow[k] for k in key))]} for lrow in left]
