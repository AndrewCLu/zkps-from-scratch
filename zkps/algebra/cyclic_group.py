from py_ecc.fields.field_elements import FQ
from algebra.field import bn128_FR, bls12_381_FR
from dataclasses import dataclass
from typing import TypeVar, Union, Any
from utils import unsigned_int_to_bytes
from abc import ABC, abstractmethod

class CyclicGroup(ABC):
    value: Any
    order: int

    @abstractmethod
    def __add__(self, other: 'CyclicGroup') -> 'CyclicGroup':
        pass

    @abstractmethod
    def __mul__(self, other: int) -> 'CyclicGroup':
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @classmethod
    @abstractmethod
    def identity(cls) -> 'CyclicGroup':
        pass

    @classmethod
    @abstractmethod
    def generator(cls) -> 'CyclicGroup':
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

@dataclass
class bn128Group(CyclicGroup):
    value: int
    order: int = bn128_FR.field_modulus

    def __add__(self, other: 'CyclicGroup') -> 'bn128Group':
        if not isinstance(other, bn128Group):
            raise Exception('Can only add bn128Group elements!')
        return bn128Group((self.value + other.value) % self.order)
    
    def __mul__(self, other: Union[int, FQ]) -> 'bn128Group':
        if isinstance(other, int):
            return bn128Group((self.value * other) % self.order)
        elif isinstance(other, FQ):
            return bn128Group((self.value * other.n) % self.order)
        else:
            raise Exception('Can only multiply bn128Group elements by ints or field elements!')

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, bn128Group):
            raise Exception('Can only compare bn128Group elements!')
        return self.value == other.value
    
    @classmethod
    def identity(cls) -> 'bn128Group':
        return bn128Group(0)

    @classmethod
    def generator(cls) -> 'bn128Group':
        return bn128Group(1)

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.value)

@dataclass
class bls12_381Group(CyclicGroup):
    value: int
    order: int = bls12_381_FR.field_modulus

    def __add__(self, other: 'CyclicGroup') -> 'bls12_381Group':
        if not isinstance(other, bls12_381Group):
            raise Exception('Can only add bls12_381Group elements!')
        return bls12_381Group((self.value + other.value) % self.order)
    
    def __mul__(self, other: Union[int, FQ]) -> 'bls12_381Group':
        if isinstance(other, int):
            return bls12_381Group((self.value * other) % self.order)
        elif isinstance(other, FQ):
            return bls12_381Group((self.value * other.n) % self.order)
        else:
            raise Exception('Can only multiply bls12_381Group elements by ints or field elements!')

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, bls12_381Group):
            raise Exception('Can only compare bls12_381Group elements!')
        return self.value == other.value
    
    @classmethod
    def identity(cls) -> 'bls12_381Group':
        return bls12_381Group(0)

    @classmethod
    def generator(cls) -> 'bls12_381Group':
        return bls12_381Group(1)

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.value)

CyclicGroupElt = TypeVar('CyclicGroupElt', bn128Group, bls12_381Group)
