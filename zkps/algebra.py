from py_ecc import bn128, bls12_381
from py_ecc.fields.field_elements import FQ
from py_ecc.typing import Field
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Type

class bn128_FR(FQ):
    field_modulus = bn128.curve_order

    def to_bytes(self) -> bytes:
        return bytes(self.n)

class bls12_381_FR(FQ):
    field_modulus = bls12_381.curve_order

    def to_bytes(self) -> bytes:
        return bytes(self.n)

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

    # TODO: FFT
    def eval_on_mult_subgroup(self, mult_subgroup: List[FElt]) -> List[FElt]:
        res = []
        for i in range(len(mult_subgroup)):
            res.append(self.__call__(mult_subgroup[i]))
        
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

    # TODO: FFT
    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        new_coeffs: List[FElt] = []
        for i in range(len(self.coeffs)):
            for j in range(len(other.coeffs)):
                index = i + j
                prod = self.coeffs[i] * self.coeffs[j]
                if index >= len(new_coeffs):
                    new_coeffs.append(prod)
                else:
                    new_coeffs[index] += prod
        
        return Polynomial[FElt](new_coeffs)

    def __truediv__(self, other: FElt) -> 'Polynomial':
        new_coeffs: List[FElt] = []
        for i in range(len(self.coeffs)):
            new_coeffs.append(self.coeffs[i] / other)
        
        return Polynomial[FElt](new_coeffs)

    # TODO: IFFT
    @staticmethod
    def interpolate_poly(domain: List[FElt], values: List[FElt], field_class: Type[FElt]) -> 'Polynomial':
        if len(domain) != len(values):
            raise Exception("Must provide number of values equal to size of domain!")

        res = Polynomial[FElt]([field_class.zero()])
        for i in range(len(domain)):
            lagrange = Polynomial[FElt]([field_class.one()])
            for j in range(len(domain)):
                if i != j:
                    lagrange *= Polynomial[FElt]([-domain[j], field_class.one()]) / (domain[i] - domain[j])
            res += Polynomial[FElt]([values[i]]) * lagrange
        
        return res
