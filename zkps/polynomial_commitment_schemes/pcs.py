from typing import Generic, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from algebra import FElt, Polynomial

@dataclass
class Commitment(ABC):
    value: Any

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

@dataclass
class Opening(ABC):
    value: Any

class PCSProver(ABC, Generic[FElt]):
    @abstractmethod
    def commit(self, f: Polynomial[FElt]) -> Commitment:
        pass

    @abstractmethod
    def open(self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any) -> Opening:
        pass

class PCSVerifier(ABC, Generic[FElt]):
    @abstractmethod
    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        pass
