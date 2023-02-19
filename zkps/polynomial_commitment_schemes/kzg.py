from __future__ import absolute_import

from typing import Generic, Any
from dataclasses import dataclass
from algebra import FElt, Polynomial
from polynomial_commitment_schemes.pcs import Commitment, Opening, PCSProver, PCSVerifier

@dataclass
class KZGCommitment(Commitment):
    NotImplemented

@dataclass
class KZGOpening(Opening):
    NotImplemented

class KZGProver(PCSProver, Generic[FElt]):
    def commit(self, f: Polynomial[FElt]) -> KZGCommitment:
        NotImplemented
    
    def open(self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any) -> KZGOpening:
        if not isinstance(cm, KZGCommitment):
            raise Exception('Wrong commitment used. Must provide a KZG commitment.')
        NotImplemented

class KZGVerifier(PCSVerifier, Generic[FElt]):
    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        if not isinstance(op, KZGOpening):
            raise Exception('Wrong opening used. Must provide a KZG opening.')
        if not isinstance(cm, KZGCommitment):
            raise Exception('Wrong commitment used. Must provide a KZG commitment.')
        NotImplemented