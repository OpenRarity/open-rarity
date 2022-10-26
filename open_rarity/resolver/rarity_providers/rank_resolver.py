from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class RankResolver(Protocol):
    @staticmethod
    @abstractmethod
    def get_all_ranks(contract_address_or_slug: str) -> dict[str, int]:
        raise NotImplementedError
