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
from py_ecc.fields.field_elements import FQ, FQ2, FQ12
from py_ecc.typing import Field, Point2D
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Type, Union, Tuple
from copy import deepcopy
from utils import Byteable, unsigned_int_to_bytes
from abc import ABC, abstractmethod

class bn128_FR(FQ, Byteable):
    field_modulus = bn128_base.curve_order
    primitive_root = 5

    @classmethod
    def get_roots_of_unity(cls, order: int) -> List['bn128_FR']:
        if (cls.field_modulus - 1) % order != 0:
            raise Exception("Order of roots of unity must divide the field modulus minus 1!")

        res = []
        root = cls(cls.primitive_root) ** ((cls.field_modulus - 1) // order)
        prod = cls.one()
        for _ in range(order):
            res.append(prod)
            prod *= root
        
        if prod != cls.one():
            raise Exception("Failed to compute valid roots of unity!")

        return res

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.n)

    def __str__(self) -> str:
        return "{n} [{mod}]".format(n = self.n, mod = self.field_modulus)

class bls12_381_FR(FQ, Byteable):
    field_modulus = bls12_381_base.curve_order
    primitive_root = 5

    @classmethod
    def get_roots_of_unity(cls, order: int) -> List['bls12_381_FR']:
        if (cls.field_modulus - 1) % order != 0:
            raise Exception("Order of roots of unity must divide the field modulus minus 1!")

        res = []
        root = cls(cls.primitive_root) ** ((cls.field_modulus - 1) // order)
        prod = cls.one()
        for _ in range(order):
            res.append(prod)
            prod *= root
        
        if prod != cls.one():
            raise Exception("Failed to compute valid roots of unity!")

        return res

    def to_bytes(self) -> bytes:
        return unsigned_int_to_bytes(self.n)

    def __str__(self) -> str:
        return "{n} [{mod}]".format(n = self.n, mod = self.field_modulus)

FElt = TypeVar('FElt', bn128_FR, bls12_381_FR)
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

@dataclass
class Polynomial(Generic[FElt]):
    coeffs: List[FElt]

    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        longer, shorter = self.coeffs, other.coeffs
        if len(self.coeffs) < len(other.coeffs):
            longer, shorter = other.coeffs, self.coeffs
        
        new_coeffs: List[FElt] = []
        for i in range(len(shorter)):
            new_coeffs.append(longer[i] + shorter[i])
        for i in range(len(shorter), len(longer)):
            new_coeffs.append(longer[i])

        # Truncate leading zeros 
        while len(new_coeffs) > 1 and new_coeffs[-1] == self.coeffs[0].zero(): ## Fix these class method calls
            new_coeffs.pop()

        return Polynomial[FElt](new_coeffs)

    def __sub__(self, other: Union[FElt, 'Polynomial']) -> 'Polynomial':
        if isinstance(other, Polynomial):
            new_coeffs: List[FElt] = []
            for i in range(min(len(self.coeffs), len(other.coeffs))):
                new_coeffs.append(self.coeffs[i] - other.coeffs[i])

            if len(self.coeffs) >= len(other.coeffs):
                for j in range(min(len(self.coeffs), len(other.coeffs)), max(len(self.coeffs), len(other.coeffs))):
                    new_coeffs.append(self.coeffs[j])
            else:
                for j in range(min(len(self.coeffs), len(other.coeffs)), max(len(self.coeffs), len(other.coeffs))):
                    new_coeffs.append(-other.coeffs[j])
            
            return Polynomial[FElt](new_coeffs)
        else:
            new_coeffs = deepcopy(self.coeffs)
            new_coeffs[0] -= other
            return Polynomial[FElt](new_coeffs)

    # TODO: FFT
    def __mul__(self, other: Union[FElt, 'Polynomial']) -> 'Polynomial':
        new_coeffs: List[FElt] = []
        if isinstance(other, Polynomial):
            for i in range(len(self.coeffs)):
                for j in range(len(other.coeffs)):
                    index = i + j
                    prod = self.coeffs[i] * other.coeffs[j]
                    if index >= len(new_coeffs):
                        new_coeffs.append(prod)
                    else:
                        new_coeffs[index] += prod
        else:
            for i in range(len(self.coeffs)):
                new_coeffs.append(other * self.coeffs[i])
        
        return Polynomial[FElt](new_coeffs)

    # Returns (quotient, remainder) after division by other
    def __truediv__(self, other: Union[FElt, 'Polynomial']) -> Tuple['Polynomial', 'Polynomial']:
        if isinstance(other, Polynomial):
            num_coeffs = deepcopy(self.coeffs)
            den_coeffs = deepcopy(other.coeffs)
            if len(num_coeffs) < len(den_coeffs):
                return (Polynomial[FElt]([self.coeffs[0].zero()]), Polynomial[FElt](num_coeffs)) # TODO: Fix these class method calls
            quo_coeffs: List[FElt] = []
            zero: FElt = self.coeffs[0].zero() # TODO: Fix these class method calls
            while len(num_coeffs) >= len(den_coeffs):
                if num_coeffs[-1] == zero:
                    quo_coeffs.insert(0, self.coeffs[0].zero()) # TODO: Fix these class method calls
                    num_coeffs.pop()
                else:
                    quo = num_coeffs[-1] / den_coeffs[-1]
                    quo_coeffs.insert(0, quo)
                    for i in range(len(den_coeffs)):
                        num_coeffs[-(1+i)] -= quo * den_coeffs[-(1+i)]
                    num_coeffs.pop()
            # Truncate leading zeros 
            while len(num_coeffs) > 1 and num_coeffs[-1] == self.coeffs[0].zero(): ## Fix these class method calls
                num_coeffs.pop()
            return (Polynomial[FElt](quo_coeffs), Polynomial[FElt](num_coeffs))
        else:
            new_coeffs: List[FElt] = []
            for i in range(len(self.coeffs)):
                new_coeffs.append(self.coeffs[i] / other)
            return (Polynomial[FElt](new_coeffs), Polynomial[FElt]([self.coeffs[0].zero()])) # TODO: Fix these class method calls

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polynomial):
            return False
        if len(self.coeffs) != len(other.coeffs):
            return False
        for i in range(len(self.coeffs)):
            if self.coeffs[i] != other.coeffs[i]:
                return False

        return True
    
    def __call__(self, x: FElt) -> FElt:
        res = x.zero()
        xs = x.one()
        for i in range(len(self.coeffs)):
            res += xs * self.coeffs[i]
            xs *= x
        
        return res

    # TODO: FFT
    def eval_on_mult_subgroup(self, mult_subgroup: List[FElt]) -> List[FElt]:
        res = []
        for i in range(len(mult_subgroup)):
            res.append(self.__call__(mult_subgroup[i]))
        
        return res

    # TODO: IFFT
    @staticmethod
    def interpolate_poly(domain: List[FElt], values: List[FElt], field_class: Type[FElt]) -> 'Polynomial':
        if len(domain) != len(values):
            raise Exception("Must provide number of values equal to size of domain!")

        res = Polynomial[FElt]([field_class.zero()])
        for i in range(len(domain)):
            lagrange = Polynomial.lagrange_poly(domain=domain, index=i, field_class=field_class)
            res += lagrange * values[i]
        
        return res

    @staticmethod
    def lagrange_poly(domain: List[FElt], index: int, field_class: Type[FElt]) -> 'Polynomial':
        if index >= len(domain):
            raise Exception("Index must be within the bounds of the domain!")

        prod = Polynomial[FElt]([field_class.one()])
        divisor = field_class.one()

        for i in range(len(domain)):
            if i != index:
                prod *= Polynomial[FElt](coeffs=[-domain[i], field_class.one()])
                divisor *= (domain[index] - domain[i])

        quo, rem = prod / divisor
        if rem != Polynomial[FElt](coeffs=[field_class.zero()]):
            raise Exception("Error computing lagrange polynomial!")
        
        return quo
        
