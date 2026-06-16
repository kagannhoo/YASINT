from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FindingResult:
    module: str
    category: str
    key: str
    value: Any
    confidence: float
    source: str
    raw_data: dict | None = field(default=None)


class BaseModule(ABC):
    """Tüm OSINT modüllerinin temel sınıfı"""

    @property
    @abstractmethod
    def module_name(self) -> str:
        pass

    @abstractmethod
    async def run(self, inputs: dict) -> list[FindingResult]:
        """
        inputs: { 'images': [...], 'username': '...', 'ip': '...', ... }
        returns: List[FindingResult]
        """
        pass
