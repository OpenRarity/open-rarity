import dataclasses
from collections.abc import Mapping
from typing import Iterator


@dataclasses.dataclass
class BaseDataClass(Mapping):  # type: ignore
    def __getitem__(self, item: str):
        return getattr(self, item)

    def __iter__(self) -> Iterator[str]:
        return (k for k in self.__dict__.keys())

    def __len__(self) -> int:
        return len(self.__dict__)


JsonContainer = list[str | float | int] | dict[str | float | int, str | float | int]

JsonEncodable = (
    list[JsonContainer | str | float | int]
    | dict[JsonContainer | str | float | int, JsonContainer | str | float | int]
    | str
    | float
    | int
)


__all__ = ["JsonEncodable"]
