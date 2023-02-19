from py_ecc import bn128, bls12_381
from py_ecc.fields.field_elements import FQ
from py_ecc.typing import Field
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Self

class bn128_FR(FQ):
    field_modulus = bn128.curve_order

class bls12_381_FR(FQ):
    field_modulus = bls12_381.curve_order

FElt = TypeVar('FElt', bn128_FR, bls12_381_FR)

@dataclass
class Polynomial(Generic[FElt]):
    coeffs: List[FElt]

    def __call__(self, x: FElt) -> FElt:
        res = x.zero()
        xs = x.one()
        for i in range(len(self.coeffs)):
            res += xs * self.coeffs[i]
            xs *= x
        
        return res

    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        longer, shorter = self.coeffs, other.coeffs
        if len(self.coeffs) < len(other.coeffs):
            longer, shorter = other.coeffs, self.coeffs
        
        new_coeffs = []
        for i in range(len(shorter)):
            new_coeffs.append(longer[i] + shorter[i])
        for i in range(len(shorter), len(longer)):
            new_coeffs.append(longer[i])

        return Polynomial[FElt](new_coeffs)

    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        new_coeffs = []
        for i in range(len(self.coeffs)):
            for j in range(len(other.coeffs)):
                index = i + j
                prod = self.coeffs[i] * self.coeffs[j]
                if index >= len(new_coeffs):
                    new_coeffs.append(prod)
                else:
                    new_coeffs[index] += prod
        
        return Polynomial[FElt](new_coeffs)

    def __div__(self, other: FElt) -> 'Polynomial':
        new_coeffs = []
        for i in range(len(self.coeffs)):
            new_coeffs.append(self.coeffs[i] / other)
        
        return Polynomial[FElt](new_coeffs)

    @staticmethod
    def interpolate_poly(domain: List[FElt], values: List[FElt]) -> 'Polynomial':
        assert(len(domain) == len(values), "Must provide number of values equal to size of domain!")

        res = Polynomial[FElt]([0])
        for i in range(len(domain)):
            lagrange = Polynomial[FElt]([1])
            for j in range(len(domain)):
                if i != j:
                    lagrange *= Polynomial[FElt]([-domain[j], 1]) / (domain[i] - domain[j])
            res += Polynomial[FElt]([values[i]]) * lagrange
        
        return res
