from typing import Hashable, TypeVar

T = TypeVar["T"]


def merge(left: list[dict], right: list[dict], key: tuple[Hashable]) -> list[dict]:
    right = {tuple((row[k] for k in key)): row for row in right}
    return [{**lrow, **right[tuple((lrow[k] for k in key))]} for lrow in left]


def rank_over(data: list[dict[str]], key=str | tuple[str, str]):
    key = (key,) if isinstance(key, str) else key

    data = sorted(data, key=lambda row: tuple((row[k] for k in key)))

    current_rank = 1
    prev_value = None
    for incremental_rank, row in enumerate(data, 1):
        data_index = incremental_rank - 1
        current_value = tuple((row[k] for k in key))

        if current_value == prev_value or incremental_rank == 1:
            data[data_index]["rank"] = current_rank
        else:
            data[data_index]["rank"] = current_rank = incremental_rank
        prev_value = current_value

    return data
