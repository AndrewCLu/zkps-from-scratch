from typing import Generic, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from algebra import FElt, Polynomial, List
from utils import Byteable

@dataclass
class Commitment(Byteable):
    value: Any

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

    @abstractmethod
    def batch_open_at_point(self, fs: List[Polynomial[FElt]], cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any) -> Opening:
        pass

class PCSVerifier(ABC, Generic[FElt]):
    @abstractmethod
    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        pass

    @abstractmethod
    def verify_batch_at_point(self, op: Opening, cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any) -> bool:
        pass
