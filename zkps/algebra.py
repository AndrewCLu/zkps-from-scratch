from py_ecc import bn128, bls12_381
from py_ecc.fields.field_elements import FQ
from py_ecc.typing import Field
from dataclasses import dataclass
from typing import TypeVar, Generic, List

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