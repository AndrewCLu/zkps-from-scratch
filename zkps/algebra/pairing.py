from py_ecc import (
    bn128 as bn128_base, 
    bls12_381 as bls12_381_base,
)
from py_ecc.fields import (
    bn128_FQ as bn128_FQ_base,
    bn128_FQ2 as bn128_FQ2_base,
    bn128_FQ12 as bn128_FQ12_base,
    bls12_381_FQ as bls12_381_FQ_base,
    bls12_381_FQ2 as bls12_381_FQ2_base,
    bls12_381_FQ12 as bls12_381_FQ12_base,
)
from py_ecc.typing import Point2D
from algebra.field import FElt
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

BaseField = TypeVar('BaseField', bn128_FQ_base, bls12_381_FQ_base)
G2Field = TypeVar('G2Field', bn128_FQ2_base, bls12_381_FQ2_base)
GtField = TypeVar('GtField', bn128_FQ12_base, bls12_381_FQ12_base)

class EllipticCurve(ABC, Generic[FElt, BaseField, G2Field, GtField]):
    g_1: Point2D[BaseField]
    g_2: Point2D[G2Field]

    @abstractmethod
    def add(self, p1: Point2D[BaseField], p2: Point2D[BaseField]) -> Point2D[BaseField]:
        pass

    @abstractmethod
    def add_G_2(self, p1: Point2D[G2Field], p2: Point2D[G2Field]) -> Point2D[G2Field]:
        pass

    @abstractmethod
    def multiply(self, p: Point2D[BaseField], n: FElt) -> Point2D[BaseField]:
        pass

    @abstractmethod
    def multiply_G_2(self, p: Point2D[G2Field], n: FElt) -> Point2D[G2Field]:
        pass

    @abstractmethod
    def identity(self) -> Point2D[BaseField]:
        pass

    @abstractmethod
    def pairing(self, p: Point2D[BaseField], q: Point2D[G2Field]) -> GtField:
        pass

class bn128(EllipticCurve):
    g_1: Point2D[bn128_FQ_base] = bn128_base.G1
    g_2: Point2D[bn128_FQ2_base] = bn128_base.G2

    @classmethod
    def add(cls, p1: Point2D[bn128_FQ_base], p2: Point2D[bn128_FQ_base]) -> Point2D[bn128_FQ_base]:
        return bn128_base.add(p1, p2)
    
    @classmethod
    def add_G_2(cls, p1: Point2D[bn128_FQ2_base], p2: Point2D[bn128_FQ2_base]) -> Point2D[bn128_FQ2_base]:
        return bn128_base.add(p1, p2)
    
    @classmethod
    def multiply(cls, p: Point2D[bn128_FQ_base], n: FElt) -> Point2D[bn128_FQ_base]:
        return bn128_base.multiply(p, n.n)

    @classmethod
    def multiply_G_2(cls, p: Point2D[bn128_FQ2_base], n: FElt) -> Point2D[bn128_FQ2_base]:
        return bn128_base.multiply(p, n.n)
    
    @classmethod
    def identity(cls) -> Point2D[bn128_FQ_base]:
        return None

    @classmethod
    def pairing(cls, p: Point2D[bn128_FQ_base], q: Point2D[bn128_FQ2_base]) -> bn128_FQ12_base:
        return bn128_base.bn128_pairing.pairing(q, p)
