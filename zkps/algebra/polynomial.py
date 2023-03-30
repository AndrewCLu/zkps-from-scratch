from typing import Generic, List, Type, Union, Tuple
from copy import deepcopy
from dataclasses import dataclass
from itertools import zip_longest
from algebra.field import FElt
from metrics import Counter


@dataclass
class Polynomial(Generic[FElt]):
    coeffs: List[FElt]

    @Counter
    def __add__(self, other: "Polynomial") -> "Polynomial":
        new_coeffs = [
            a + b
            for a, b in zip_longest(
                self.coeffs, other.coeffs, fillvalue=self.coeffs[0].zero()
            )
        ]

        # Truncate leading zeros
        while len(new_coeffs) > 1 and new_coeffs[-1] == self.coeffs[0].zero():
            new_coeffs.pop()

        return Polynomial[FElt](new_coeffs)

    @Counter
    def __sub__(self, other: Union[FElt, "Polynomial"]) -> "Polynomial":
        if isinstance(other, Polynomial):
            new_coeffs: List[FElt] = []
            for i in range(min(len(self.coeffs), len(other.coeffs))):
                new_coeffs.append(self.coeffs[i] - other.coeffs[i])

            if len(self.coeffs) >= len(other.coeffs):
                for j in range(
                    min(len(self.coeffs), len(other.coeffs)),
                    max(len(self.coeffs), len(other.coeffs)),
                ):
                    new_coeffs.append(self.coeffs[j])
            else:
                for j in range(
                    min(len(self.coeffs), len(other.coeffs)),
                    max(len(self.coeffs), len(other.coeffs)),
                ):
                    new_coeffs.append(-other.coeffs[j])

            return Polynomial[FElt](new_coeffs)
        else:
            new_coeffs = deepcopy(self.coeffs)
            new_coeffs[0] -= other
            return Polynomial[FElt](new_coeffs)

    # TODO: FFT
    @Counter
    def __mul__(self, other: Union[FElt, "Polynomial"]) -> "Polynomial":
        new_coeffs: List[FElt] = []
        if isinstance(other, Polynomial):
            for i, self_coeff in enumerate(self.coeffs):
                for j, other_coeff in enumerate(other.coeffs):
                    index = i + j
                    prod = self_coeff * other_coeff
                    if index >= len(new_coeffs):
                        new_coeffs.append(prod)
                    else:
                        new_coeffs[index] += prod
        else:
            for coeff in self.coeffs:
                new_coeffs.append(other * coeff)

        return Polynomial[FElt](new_coeffs)

    # Returns (quotient, remainder) after division by other
    @Counter
    def __truediv__(
        self, other: Union[FElt, "Polynomial"]
    ) -> Tuple["Polynomial", "Polynomial"]:
        if isinstance(other, Polynomial):
            num_coeffs = deepcopy(self.coeffs)
            den_coeffs = deepcopy(other.coeffs)
            if len(num_coeffs) < len(den_coeffs):
                return (
                    Polynomial[FElt]([self.coeffs[0].zero()]),
                    Polynomial[FElt](num_coeffs),
                )
            quo_coeffs: List[FElt] = []
            zero: FElt = self.coeffs[0].zero()
            while len(num_coeffs) >= len(den_coeffs):
                if num_coeffs[-1] == zero:
                    quo_coeffs.insert(0, self.coeffs[0].zero())
                    num_coeffs.pop()
                else:
                    quo = num_coeffs[-1] / den_coeffs[-1]
                    quo_coeffs.insert(0, quo)
                    for i in range(len(den_coeffs)):
                        num_coeffs[-(1 + i)] -= quo * den_coeffs[-(1 + i)]
                    num_coeffs.pop()
            # Truncate leading zeros
            while len(num_coeffs) > 1 and num_coeffs[-1] == self.coeffs[0].zero():
                num_coeffs.pop()
            return (Polynomial[FElt](quo_coeffs), Polynomial[FElt](num_coeffs))
        else:
            new_coeffs: List[FElt] = []
            for coeff in self.coeffs:
                new_coeffs.append(coeff / other)
            return (
                Polynomial[FElt](new_coeffs),
                Polynomial[FElt]([self.coeffs[0].zero()]),
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polynomial):
            return False
        if len(self.coeffs) != len(other.coeffs):
            return False
        for i, coeff in enumerate(self.coeffs):
            if coeff != other.coeffs[i]:
                return False

        return True

    @Counter
    def __call__(self, x: FElt) -> FElt:
        res = x.zero()
        xs = x.one()
        for coeff in self.coeffs:
            res += xs * coeff
            xs *= x

        return res

    # TODO: FFT
    def eval_on_mult_subgroup(self, mult_subgroup: List[FElt]) -> List[FElt]:
        return [self(x) for x in mult_subgroup]

    # TODO: IFFT
    @staticmethod
    @Counter
    def interpolate_poly(
        domain: List[FElt], values: List[FElt], field_class: Type[FElt]
    ) -> "Polynomial":
        if len(domain) != len(values):
            raise ValueError("Must provide number of values equal to size of domain!")

        res = Polynomial[FElt]([field_class.zero()])
        for i in range(len(domain)):
            lagrange = Polynomial.lagrange_poly(
                domain=domain, index=i, field_class=field_class
            )
            res += lagrange * values[i]

        return res

    @staticmethod
    @Counter
    def lagrange_poly(
        domain: List[FElt], index: int, field_class: Type[FElt]
    ) -> "Polynomial":
        if index >= len(domain):
            raise ValueError("Index must be within the bounds of the domain!")

        prod = Polynomial[FElt]([field_class.one()])
        divisor = field_class.one()

        for i, value in enumerate(domain):
            if i != index:
                prod *= Polynomial[FElt](coeffs=[-value, field_class.one()])
                divisor *= domain[index] - value

        quo, rem = prod / divisor
        if rem != Polynomial[FElt](coeffs=[field_class.zero()]):
            raise ValueError("Error computing lagrange polynomial!")

        return quo
