from py_ecc import bn128, bls12_381
from py_ecc.fields.field_elements import FQ
from py_ecc.typing import Field
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Type, Union, Tuple
from copy import deepcopy

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

    # TODO: Auto truncate zero leading coeffs in poly
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
    def __mul__(self, other: Union[FElt, 'Polynomial']) -> 'Polynomial':
        new_coeffs: List[FElt] = []
        if isinstance(other, FElt):
            for i in range(len(self.coeffs)):
                new_coeffs.append(other * self.coeffs[i])
        elif isinstance(other, Polynomial):
            for i in range(len(self.coeffs)):
                for j in range(len(other.coeffs)):
                    index = i + j
                    prod = self.coeffs[i] * self.coeffs[j]
                    if index >= len(new_coeffs):
                        new_coeffs.append(prod)
                    else:
                        new_coeffs[index] += prod
        else:
            raise Exception('Argument to mul must be a field element or polynomial!')
        
        return Polynomial[FElt](new_coeffs)

    # Returns (quotient, remainder) after division by other
    def __truediv__(self, other: Union[FElt, 'Polynomial']) -> Tuple['Polynomial', 'Polynomial']:
        if isinstance(other, FElt):
            new_coeffs: List[FElt] = []
            for i in range(len(self.coeffs)):
                new_coeffs.append(self.coeffs[i] / other)
            return (Polynomial[FElt](new_coeffs), Polynomial[FElt]([self.coeffs[0].zero()])) # TODO: Fix these class method calls
        elif isinstance(other, Polynomial):
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
                    for i in range(len(quo_coeffs)):
                        num_coeffs[-(1+i)] -= quo * den_coeffs[-(1+i)]
                    num_coeffs.pop()
            return (Polynomial[FElt](quo_coeffs), Polynomial[FElt](num_coeffs))
        else:
            raise Exception('Argument to div must be a field element or polynomial!')

    # TODO: IFFT
    @staticmethod
    def interpolate_poly(domain: List[FElt], values: List[FElt], field_class: Type[FElt]) -> 'Polynomial':
        if len(domain) != len(values):
            raise Exception("Must provide number of values equal to size of domain!")

        res = Polynomial[FElt]([field_class.zero()])
        for i in range(len(domain)):
            lagrange = Polynomial.lagrange_poly(domain=domain, index=i, field_class=field_class)
            res += Polynomial[FElt]([values[i]]) * lagrange
        
        return res

    @staticmethod
    def lagrange_poly(domain: List[FElt], index: int, field_class: Type[FElt]) -> 'Polynomial':
        if index >= len(domain):
            raise Exception("Index must be within the bounds of the domain!")

        res = Polynomial[FElt]([field_class.one()])
        for i in range(len(domain)):
            if i != index:
                quo, _ = Polynomial[FElt]([-domain[i], field_class.one()]) / (domain[index] - domain[i])
                res *= quo
        
        return res
        
