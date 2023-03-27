from typing import Generic, List, Type, Union, Tuple
from copy import deepcopy
from dataclasses import dataclass
from algebra.field import FElt
from metrics import Counter


@dataclass
class Polynomial(Generic[FElt]):
    coeffs: List[FElt]

    def __add__(self, other: "Polynomial") -> "Polynomial":
        longer, shorter = self.coeffs, other.coeffs
        if len(self.coeffs) < len(other.coeffs):
            longer, shorter = other.coeffs, self.coeffs

        new_coeffs: List[FElt] = []
        for i in range(len(shorter)):
            new_coeffs.append(longer[i] + shorter[i])
        for i in range(len(shorter), len(longer)):
            new_coeffs.append(longer[i])

        # Truncate leading zeros
        while (
            len(new_coeffs) > 1 and new_coeffs[-1] == self.coeffs[0].zero()
        ):  ## Fix these class method calls
            new_coeffs.pop()

        return Polynomial[FElt](new_coeffs)

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
    def __mul__(self, other: Union[FElt, "Polynomial"]) -> "Polynomial":
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
                )  # TODO: Fix these class method calls
            quo_coeffs: List[FElt] = []
            zero: FElt = self.coeffs[0].zero()  # TODO: Fix these class method calls
            while len(num_coeffs) >= len(den_coeffs):
                if num_coeffs[-1] == zero:
                    quo_coeffs.insert(
                        0, self.coeffs[0].zero()
                    )  # TODO: Fix these class method calls
                    num_coeffs.pop()
                else:
                    quo = num_coeffs[-1] / den_coeffs[-1]
                    quo_coeffs.insert(0, quo)
                    for i in range(len(den_coeffs)):
                        num_coeffs[-(1 + i)] -= quo * den_coeffs[-(1 + i)]
                    num_coeffs.pop()
            # Truncate leading zeros
            while (
                len(num_coeffs) > 1 and num_coeffs[-1] == self.coeffs[0].zero()
            ):  ## Fix these class method calls
                num_coeffs.pop()
            return (Polynomial[FElt](quo_coeffs), Polynomial[FElt](num_coeffs))
        else:
            new_coeffs: List[FElt] = []
            for i in range(len(self.coeffs)):
                new_coeffs.append(self.coeffs[i] / other)
            return (
                Polynomial[FElt](new_coeffs),
                Polynomial[FElt]([self.coeffs[0].zero()]),
            )  # TODO: Fix these class method calls

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

        for i in range(len(domain)):
            if i != index:
                prod *= Polynomial[FElt](coeffs=[-domain[i], field_class.one()])
                divisor *= domain[index] - domain[i]

        quo, rem = prod / divisor
        if rem != Polynomial[FElt](coeffs=[field_class.zero()]):
            raise ValueError("Error computing lagrange polynomial!")

        return quo
