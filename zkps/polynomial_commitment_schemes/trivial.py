from __future__ import absolute_import

from typing import Generic, Any, List, cast
from dataclasses import dataclass
from algebra.field import FElt
from algebra.polynomial import Polynomial
from polynomial_commitment_schemes.pcs import (
    Commitment,
    Opening,
    PCSProver,
    PCSVerifier,
)
from utils import Byteable


@dataclass
class TrivialCommitment(Commitment, Byteable, Generic[FElt]):
    value: List[FElt]

    def to_bytes(self) -> bytes:
        res = bytearray()
        for i in range(len(self.value)):
            res.extend(self.value[i].to_bytes())

        return bytes(res)

    def __str__(self) -> str:
        return ", ".join([str(x) for x in self.value])


@dataclass
class TrivialOpening(Opening):
    value: None


class TrivialProver(PCSProver, Generic[FElt]):
    def commit(self, f: Polynomial[FElt]) -> TrivialCommitment[FElt]:
        return TrivialCommitment[FElt](value=f.coeffs)

    def open(
        self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any
    ) -> TrivialOpening:
        if not isinstance(cm, TrivialCommitment):
            raise Exception("Wrong commitment used. Must provide a trivial commitment.")
        return TrivialOpening(value=None)

    def batch_open_at_point(
        self,
        fs: List[Polynomial[FElt]],
        cms: List[Commitment],
        z: FElt,
        ss: List[FElt],
        op_info: Any,
    ) -> Opening:
        batch_size = len(fs)
        if len(cms) != batch_size or len(ss) != batch_size:
            raise Exception("All parameters must have length equal to batch size!")

        return TrivialOpening(value=None)


class TrivialVerifier(PCSVerifier, Generic[FElt]):
    def verify_opening(
        self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any
    ) -> bool:
        if not isinstance(op, TrivialOpening):
            raise Exception("Wrong opening used. Must provide a trivial opening.")
        if not isinstance(cm, TrivialCommitment):
            raise Exception("Wrong commitment used. Must provide a trivial commitment.")
        coeffs: List[FElt] = cast(TrivialCommitment[FElt], cm).value
        f = Polynomial[FElt](coeffs=coeffs)
        return f(z) == s

    def verify_batch_at_point(
        self, op: Opening, cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any
    ) -> bool:
        if not isinstance(op, TrivialOpening):
            raise Exception("Wrong opening used. Must provide a trivial opening.")

        batch_size = len(cms)
        if len(ss) != batch_size:
            raise Exception("All parameters must have length equal to batch size!")

        for i in range(batch_size):
            if not isinstance(cms[i], TrivialCommitment):
                raise Exception(
                    "Wrong commitment used. Must provide a trivial commitment."
                )

        for i in range(batch_size):
            if not self.verify_opening(op=op, cm=cms[i], z=z, s=ss[i], op_info=op_info):
                return False

        return True
