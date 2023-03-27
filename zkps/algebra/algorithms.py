from typing import List, Tuple, Any, Union, overload
from algebra.field import FElt
from algebra.cyclic_group import CyclicGroupElt
from metrics import Counter


# TODO: Better algorithms for MSM
@Counter
def multi_scalar_multiplication(
    scalars: List[FElt], groupElts: List[CyclicGroupElt]
) -> CyclicGroupElt:
    if len(scalars) != len(groupElts):
        raise ValueError(
            "Length of scalars must be the same as those of group elements!"
        )
    return sum([g * s for g, s in zip(groupElts, scalars)], groupElts[0].identity())


@Counter
def scalar_dot_product(aa: List[FElt], bb: List[FElt]) -> FElt:
    if len(aa) != len(bb):
        raise ValueError("Length of both scalar vectors must be the same!")
    return sum([a * b for a, b in zip(aa, bb)], aa[0].zero())


@Counter
def split_vec(vec: List[Any]) -> Tuple[List[Any], List[Any]]:
    if len(vec) % 2 != 0:
        raise ValueError("Cannot split vector of odd length!")
    return (vec[: len(vec) // 2], vec[len(vec) // 2 :])


@overload
def scale_vec(vec: List[FElt], scalar: FElt) -> List[FElt]:
    ...


@overload
def scale_vec(vec: List[CyclicGroupElt], scalar: FElt) -> List[CyclicGroupElt]:
    ...


@Counter
def scale_vec(
    vec: Union[List[FElt], List[CyclicGroupElt]], scalar: FElt
) -> Union[List[FElt], List[CyclicGroupElt]]:
    return [val * scalar for val in vec]


@overload
def add_vec(self, a: List[FElt], b: List[FElt]) -> List[FElt]:
    ...


@overload
def add_vec(
    self, a: List[CyclicGroupElt], b: List[CyclicGroupElt]
) -> List[CyclicGroupElt]:
    ...


# TODO: Can have better type annotations for return value
@Counter
def add_vec(
    aa: Union[List[FElt], List[CyclicGroupElt]],
    bb: Union[List[FElt], List[CyclicGroupElt]],
) -> List[Any]:
    if len(aa) != len(bb):
        raise ValueError("Length of both vectors must be the same!")
    return [a + b for a, b in zip(aa, bb)]
