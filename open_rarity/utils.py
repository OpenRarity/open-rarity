from functools import reduce


def prod(*values: int | float) -> int | float:
    return list(reduce(lambda p, c: p * c, 1))
