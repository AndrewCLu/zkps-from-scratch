from __future__ import absolute_import

import random
from typing import Generic, Any, List, Type
from py_ecc.typing import Point2D
from dataclasses import dataclass
from algebra import FElt, Polynomial, EllipticCurve, BaseField, G2Field, GtField
from polynomial_commitment_schemes.pcs import Commitment, Opening, PCSProver, PCSVerifier
from utils import unsigned_int_to_bytes

@dataclass
class KZGSRS(Generic[FElt, BaseField, G2Field, GtField]):
    G_1_elts: List[Point2D[BaseField]]
    G_2_elts: List[Point2D[G2Field]]

    @staticmethod
    # This is not secure since we are generating deterministically
    def trusted_setup(d: int, ec: EllipticCurve[FElt, BaseField, G2Field, GtField], field_class: Type[FElt]) -> 'KZGSRS':
        s: FElt = field_class(random.randint(1, field_class.field_modulus - 1))
        G_1_elts = [ec.g_1] 
        for _ in range(d-1):
            G_1_elts.append(ec.multiply(G_1_elts[-1], s))
        G_2_elts = [ec.g_2, ec.multiply_G_2(ec.g_2, s)]

        return KZGSRS(
            G_1_elts=G_1_elts,
            G_2_elts=G_2_elts
        )

@dataclass
class KZGCommitment(Commitment, Generic[BaseField]):
    value: Point2D[BaseField]

    # TODO: Attach these methods to the field elements instead
    def to_bytes(self) -> bytes:
        if self.value is None:
            return bytes(0)
        else:
            res = bytearray()
            res.extend(unsigned_int_to_bytes(self.value[0].n))            
            res.extend(unsigned_int_to_bytes(self.value[1].n))
            return bytes(res)

@dataclass
class KZGOpening(Opening, Generic[BaseField]):
    value: Point2D[BaseField]

class KZGProver(PCSProver, Generic[FElt, BaseField, G2Field, GtField]):
    def __init__(self, ec: EllipticCurve[FElt, BaseField, G2Field, GtField], srs: KZGSRS):
        self.ec: EllipticCurve[FElt, BaseField, G2Field, GtField] = ec
        self.srs: KZGSRS = srs

    def __eval_poly_with_srs(self, f: Polynomial[FElt]) -> Point2D[BaseField]:
        res = self.ec.identity()
        for i in range(len(f.coeffs)):
            eval = self.ec.multiply(self.srs.G_1_elts[i], f.coeffs[i])
            res = self.ec.add(res, eval)
        
        return res

    def commit(self, f: Polynomial[FElt]) -> KZGCommitment:
        if len(f.coeffs) > len(self.srs.G_1_elts):
            raise Exception("Polynomial degree is greater than size of SRS!")

        cm = self.__eval_poly_with_srs(f)
        
        return KZGCommitment(value=cm)
    
    def open(self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any) -> KZGOpening:
        if not isinstance(cm, KZGCommitment):
            raise Exception("Wrong commitment used. Must provide a KZG commitment.")
                
        quo, rem = (f - s) / Polynomial[FElt](coeffs=[-z, f.coeffs[0].one()]) # TODO: Remove reference to class through instance
        if rem != Polynomial[FElt](coeffs=[f.coeffs[0].zero()]): # TODO: Remove reference to class through instance
            raise Exception("Opening is not valid: f(z) != s")
        op = self.__eval_poly_with_srs(quo)

        return KZGOpening(value=op)
    
    def batch_open_at_point(self, fs: List[Polynomial[FElt]], cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any) -> Opening:
        batch_size = len(fs)
        if len(cms) != batch_size or len(ss) != batch_size:
            raise Exception('All parameters must have length equal to batch size!')
        
        sum = Polynomial[FElt](coeffs=[fs[0].coeffs[0].zero()]) # TODO: Remove reference to class through instance
        scalar = fs[0].coeffs[0].one() # TODO: Remove reference to class through instance
        for i in range(batch_size):
            if not isinstance(cms[i], KZGCommitment):
                raise Exception("Wrong commitment used. Must provide a KZG commitment.")

            quo, rem = (fs[i] - ss[i]) / Polynomial[FElt](coeffs=[-z, fs[i].coeffs[0].one()]) # TODO: Remove reference to class through instance
            if rem != Polynomial[FElt](coeffs=[fs[i].coeffs[0].zero()]): # TODO: Remove reference to class through instance
                raise Exception("Opening is not valid: f(z) != s")

            sum += quo * scalar
            # TODO: Missing check that op_info is of type FElt
            scalar *= op_info
        
        op = self.__eval_poly_with_srs(sum)

        return KZGOpening(value=op) 

class KZGVerifier(PCSVerifier, Generic[FElt, BaseField, G2Field, GtField]):
    def __init__(self, ec: EllipticCurve[FElt, BaseField, G2Field, GtField], srs: KZGSRS):
        self.ec: EllipticCurve[FElt, BaseField, G2Field, GtField] = ec
        self.srs: KZGSRS = srs

    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        if not isinstance(op, KZGOpening):
            raise Exception("Wrong opening used. Must provide a KZG opening.")
        if not isinstance(cm, KZGCommitment):
            raise Exception("Wrong commitment used. Must provide a KZG commitment.")
        
        lhs = self.ec.pairing(op.value, self.ec.add_G_2(self.srs.G_2_elts[1], self.ec.multiply_G_2(self.srs.G_2_elts[0], -z)))
        rhs = self.ec.pairing(self.ec.add(cm.value, self.ec.multiply(self.srs.G_1_elts[0], -s)), self.srs.G_2_elts[0])
        return lhs == rhs

    def verify_batch_at_point(self, op: Opening, cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any) -> bool:
        if not isinstance(op, KZGOpening):
            raise Exception('Wrong opening used. Must provide a KZG opening.')
        
        batch_size = len(cms)
        if len(ss) != batch_size:
            raise Exception('All parameters must have length equal to batch size!')

        for i in range(batch_size):
            if not isinstance(cms[i], KZGCommitment):
                raise Exception('Wrong commitment used. Must provide a KZG commitment.')

        cm_sum = None # EC identity point
        v_sum = z.zero() # TODO: Remove reference to class through instance
        scalar = z.one() # TODO: Remove reference to class through instance
        for i in range(batch_size):
            cm_sum = self.ec.add(cm_sum, self.ec.multiply(cms[i].value, scalar))
            v_sum += ss[i] * scalar

            # TODO: Missing check that op_info is of type FElt
            scalar *= op_info
        
        lhs = self.ec.pairing(op.value, self.ec.add_G_2(self.srs.G_2_elts[1], self.ec.multiply_G_2(self.srs.G_2_elts[0], -z)))
        rhs = self.ec.pairing(self.ec.add(cm_sum, self.ec.multiply(self.srs.G_1_elts[0], -v_sum)), self.srs.G_2_elts[0])
        return lhs == rhs