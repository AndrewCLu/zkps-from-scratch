from dataclasses import dataclass
from typing import List, Generic
from algebra import FElt

@dataclass
class PlonkConstraints(Generic[FElt]):
    m: int
    n: int
    a: List[FElt]
    b: List[FElt]
    c: List[FElt]
    qL: List[FElt]
    qR: List[FElt]
    qO: List[FElt]
    qM: List[FElt]
    qC: List[FElt]

    def is_valid_constraint(self) -> bool:
        NotImplemented