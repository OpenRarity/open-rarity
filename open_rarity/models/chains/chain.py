from dataclasses import dataclass
from enum import Enum


@dataclass
class Chain(Enum):
    """ENUM represents the blockchain."""

    ETH = 1
