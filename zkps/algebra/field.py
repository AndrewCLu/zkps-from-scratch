from typing import List, TypeVar
from py_ecc import (
    bn128 as bn128_base,
    bls12_381 as bls12_381_base,
)
from py_ecc.fields.field_elements import FQ
from utils import Byteable, unsigned_int_to_bytes


class bn128_FR(FQ, Byteable):
    field_modulus = bn128_base.curve_order
    primitive_root = 5

    @classmethod
    def get_roots_of_unity(cls, order: int) -> List["bn128_FR"]:
        if (cls.field_modulus - 1) % order != 0:
            raise ValueError(
                "Order of roots of unity must divide the field modulus minus 1!"
            )

        res = []
        root = cls(cls.primitive_root) ** ((cls.field_modulus - 1) // order)
        prod = cls.one()
        for _ in range(order):
            res.append(prod)
            prod *= root

        if prod != cls.one():
            raise AssertionError("Failed to compute valid roots of unity!")

        return res

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.n)

    def __str__(self) -> str:
        return f"{self.n} [{self.field_modulus}]"


class bls12_381_FR(FQ, Byteable):
    field_modulus = bls12_381_base.curve_order
    primitive_root = 5

    @classmethod
    def get_roots_of_unity(cls, order: int) -> List["bls12_381_FR"]:
        if (cls.field_modulus - 1) % order != 0:
            raise ValueError(
                "Order of roots of unity must divide the field modulus minus 1!"
            )

        res = []
        root = cls(cls.primitive_root) ** ((cls.field_modulus - 1) // order)
        prod = cls.one()
        for _ in range(order):
            res.append(prod)
            prod *= root

        if prod != cls.one():
            raise AssertionError("Failed to compute valid roots of unity!")

        return res

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.n)

    def __str__(self) -> str:
        return f"{self.n} [{self.field_modulus}]"


FElt = TypeVar("FElt", bn128_FR, bls12_381_FR)
