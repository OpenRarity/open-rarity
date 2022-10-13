from abc import abstractmethod
from typing import Protocol


class RankResolver(Protocol):
    @staticmethod
    @abstractmethod
    def get_all_ranks(contract_address: str | None, slug: str | None) -> dict[str, int]:
        raise NotImplementedError
