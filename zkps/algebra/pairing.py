from typing import TypeVar, Generic
from abc import ABC, abstractmethod
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

BaseField = TypeVar("BaseField", bn128_FQ_base, bls12_381_FQ_base)
G2Field = TypeVar("G2Field", bn128_FQ2_base, bls12_381_FQ2_base)
GtField = TypeVar("GtField", bn128_FQ12_base, bls12_381_FQ12_base)


class Pairing(ABC, Generic[FElt, BaseField, G2Field, GtField]):
    g_1: Point2D[BaseField]
    g_2: Point2D[G2Field]

    @staticmethod
    @abstractmethod
    def add(p1: Point2D[BaseField], p2: Point2D[BaseField]) -> Point2D[BaseField]:
        pass

    @staticmethod
    @abstractmethod
    def add_G_2(p1: Point2D[G2Field], p2: Point2D[G2Field]) -> Point2D[G2Field]:
        pass

    @staticmethod
    @abstractmethod
    def multiply(p: Point2D[BaseField], n: FElt) -> Point2D[BaseField]:
        pass

    @staticmethod
    @abstractmethod
    def multiply_G_2(p: Point2D[G2Field], n: FElt) -> Point2D[G2Field]:
        pass

    @staticmethod
    @abstractmethod
    def identity() -> Point2D[BaseField]:
        pass

    @staticmethod
    @abstractmethod
    def pairing(p: Point2D[BaseField], q: Point2D[G2Field]) -> GtField:
        pass


class bn128_pairing(Pairing):
    g_1: Point2D[bn128_FQ_base] = bn128_base.G1
    g_2: Point2D[bn128_FQ2_base] = bn128_base.G2

    @staticmethod
    def add(
        p1: Point2D[bn128_FQ_base], p2: Point2D[bn128_FQ_base]
    ) -> Point2D[bn128_FQ_base]:
        return bn128_base.add(p1, p2)

    @staticmethod
    def add_G_2(
        p1: Point2D[bn128_FQ2_base], p2: Point2D[bn128_FQ2_base]
    ) -> Point2D[bn128_FQ2_base]:
        return bn128_base.add(p1, p2)

    @staticmethod
    def multiply(p: Point2D[bn128_FQ_base], n: FElt) -> Point2D[bn128_FQ_base]:
        return bn128_base.multiply(p, n.n)

    @staticmethod
    def multiply_G_2(p: Point2D[bn128_FQ2_base], n: FElt) -> Point2D[bn128_FQ2_base]:
        return bn128_base.multiply(p, n.n)

    @staticmethod
    def identity() -> Point2D[bn128_FQ_base]:
        return None

    @staticmethod
    def pairing(
        p: Point2D[bn128_FQ_base], q: Point2D[bn128_FQ2_base]
    ) -> bn128_FQ12_base:
        return bn128_base.bn128_pairing.pairing(q, p)


class bls12_381_pairing(Pairing):
    g_1: Point2D[bls12_381_FQ_base] = bls12_381_base.G1
    g_2: Point2D[bls12_381_FQ2_base] = bls12_381_base.G2

    @staticmethod
    def add(
        p1: Point2D[bls12_381_FQ_base], p2: Point2D[bls12_381_FQ_base]
    ) -> Point2D[bls12_381_FQ_base]:
        return bls12_381_base.add(p1, p2)

    @staticmethod
    def add_G_2(
        p1: Point2D[bls12_381_FQ2_base], p2: Point2D[bls12_381_FQ2_base]
    ) -> Point2D[bls12_381_FQ2_base]:
        return bls12_381_base.add(p1, p2)

    @staticmethod
    def multiply(p: Point2D[bls12_381_FQ_base], n: FElt) -> Point2D[bls12_381_FQ_base]:
        return bls12_381_base.multiply(p, n.n)

    @staticmethod
    def multiply_G_2(
        p: Point2D[bls12_381_FQ2_base], n: FElt
    ) -> Point2D[bls12_381_FQ2_base]:
        return bls12_381_base.multiply(p, n.n)

    @staticmethod
    def identity() -> Point2D[bls12_381_FQ_base]:
        return None

    @staticmethod
    def pairing(
        p: Point2D[bls12_381_FQ_base], q: Point2D[bls12_381_FQ2_base]
    ) -> bls12_381_FQ12_base:
        return bls12_381_base.bls12_381_pairing.pairing(q, p)
