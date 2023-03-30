from dataclasses import dataclass
from typing import TypeVar, Union, Any
from abc import ABC, abstractmethod
from py_ecc.fields.field_elements import FQ
from algebra.field import bn128_FR, bls12_381_FR
from utils import unsigned_int_to_bytes
from metrics import Counter


class CyclicGroup(ABC):
    value: Any
    order: int

    @abstractmethod
    def __add__(self, other: "CyclicGroup") -> "CyclicGroup":
        pass

    @abstractmethod
    def __mul__(self, other: int) -> "CyclicGroup":
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @classmethod
    @abstractmethod
    def identity(cls) -> "CyclicGroup":
        pass

    @classmethod
    @abstractmethod
    def generator(cls) -> "CyclicGroup":
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass


@dataclass
class bn128_group(CyclicGroup):
    value: int
    order: int = bn128_FR.field_modulus

    @Counter
    def __add__(self, other: "CyclicGroup") -> "bn128_group":
        if not isinstance(other, bn128_group):
            raise ValueError("Can only add bn128_group elements!")
        return bn128_group((self.value + other.value) % self.order)

    @Counter
    def __mul__(self, other: Union[int, FQ]) -> "bn128_group":
        if isinstance(other, int):
            return bn128_group((self.value * other) % self.order)
        elif isinstance(other, FQ):
            return bn128_group((self.value * other.n) % self.order)
        else:
            raise ValueError(
                "Can only multiply bn128_group elements by ints or field elements!"
            )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, bn128_group):
            raise ValueError("Can only compare bn128_group elements!")
        return self.value == other.value

    @classmethod
    def identity(cls) -> "bn128_group":
        return bn128_group(0)

    @classmethod
    def generator(cls) -> "bn128_group":
        return bn128_group(1)

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.value)


@dataclass
class bls12_381_group(CyclicGroup):
    value: int
    order: int = bls12_381_FR.field_modulus

    @Counter
    def __add__(self, other: "CyclicGroup") -> "bls12_381_group":
        if not isinstance(other, bls12_381_group):
            raise ValueError("Can only add bls12_381_group elements!")
        return bls12_381_group((self.value + other.value) % self.order)

    @Counter
    def __mul__(self, other: Union[int, FQ]) -> "bls12_381_group":
        if isinstance(other, int):
            return bls12_381_group((self.value * other) % self.order)
        elif isinstance(other, FQ):
            return bls12_381_group((self.value * other.n) % self.order)
        else:
            raise ValueError(
                "Can only multiply bls12_381_group elements by ints or field elements!"
            )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, bls12_381_group):
            raise ValueError("Can only compare bls12_381_group elements!")
        return self.value == other.value

    @classmethod
    def identity(cls) -> "bls12_381_group":
        return bls12_381_group(0)

    @classmethod
    def generator(cls) -> "bls12_381_group":
        return bls12_381_group(1)

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.value)


CyclicGroupElt = TypeVar("CyclicGroupElt", bn128_group, bls12_381_group)
