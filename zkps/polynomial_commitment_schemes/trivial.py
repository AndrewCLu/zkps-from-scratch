from __future__ import absolute_import

from typing import Generic, Any, List, cast
from dataclasses import dataclass
from algebra import FElt, Polynomial
from polynomial_commitment_schemes.pcs import Commitment, Opening, PCSProver, PCSVerifier

@dataclass
class TrivialCommitment(Commitment, Generic[FElt]):
    value: List[FElt]

    def to_bytes(self) -> bytes:
        res = bytearray()
        for i in range(len(self.value)):
            res.extend(self.value[i].to_bytes)
        
        return bytes(res)

@dataclass
class TrivialOpening(Opening):
    value: None

class TrivialProver(PCSProver, Generic[FElt]):
    def commit(self, f: Polynomial[FElt]) -> TrivialCommitment:
        return TrivialCommitment(value=f.coeffs)
    
    def open(self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any) -> TrivialOpening:
        if not isinstance(cm, TrivialCommitment):
            raise Exception('Wrong commitment used. Must provide a trivial commitment.')
        return TrivialOpening(value=None)

class TrivialVerifier(PCSVerifier, Generic[FElt]):
    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        if not isinstance(op, TrivialOpening):
            raise Exception('Wrong opening used. Must provide a trivial opening.')
        if not isinstance(cm, TrivialCommitment):
            raise Exception('Wrong commitment used. Must provide a trivial commitment.')
        coeffs: List[FElt] = cast(TrivialCommitment[FElt], cm).value
        f = Polynomial[FElt](coeffs=coeffs)
        return f(z) == s