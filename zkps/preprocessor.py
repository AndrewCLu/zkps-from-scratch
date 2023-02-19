from dataclasses import dataclass
from typing import Generic
from algebra import FElt, Polynomial
from constraints import PlonkConstraints

@dataclass
class PlonkPreprocessedInput(Generic[FElt]):
    PqM: Polynomial[FElt]
    PqL: Polynomial[FElt]
    PqR: Polynomial[FElt]
    PqO: Polynomial[FElt]
    PqC: Polynomial[FElt]
    S1: Polynomial[FElt]
    S2: Polynomial[FElt]
    S3: Polynomial[FElt]


def preprocess_plonk_constraints(constraints: PlonkConstraints) -> PlonkPreprocessedInput:
    NotImplemented