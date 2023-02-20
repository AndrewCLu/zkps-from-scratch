from dataclasses import dataclass
from typing import Generic, List, Type
from algebra import FElt, Polynomial
from constraints import PlonkConstraints

@dataclass
class PlonkPreprocessedInput(Generic[FElt]):
    PqL: Polynomial[FElt]
    PqR: Polynomial[FElt]
    PqO: Polynomial[FElt]
    PqM: Polynomial[FElt]
    PqC: Polynomial[FElt]
    Sid1: Polynomial[FElt]
    Sid2: Polynomial[FElt]
    Sid3: Polynomial[FElt]
    S1: Polynomial[FElt]
    S2: Polynomial[FElt]
    S3: Polynomial[FElt]

class Preprocessor(Generic[FElt]):
    @staticmethod
    def preprocess_plonk_constraints(constraints: PlonkConstraints, mult_subgroup: List[FElt], field_class: Type[FElt]) -> 'PlonkPreprocessedInput':
        permutation = Preprocessor.get_permutation_from_constraints(constraints)
        s_id_polys = []
        s_sigma_polys = []
        for j in range(3): # Follow index notation from paper
            s_id_values = []
            s_sigma_values = []
            for i in range(constraints.n):
                index = j * constraints.n + i
                s_id_values.append(field_class(index))
                s_sigma_values.append(field_class(permutation[index]))
            
            s_id_polys.append(Polynomial.interpolate_poly(domain=mult_subgroup, values=s_id_values, field_class=field_class))
            s_sigma_polys.append(Polynomial.interpolate_poly(domain=mult_subgroup, values=s_sigma_values, field_class=field_class))
        
        PqL = Polynomial.interpolate_poly(domain=mult_subgroup, values=constraints.qL, field_class=field_class)
        PqR = Polynomial.interpolate_poly(domain=mult_subgroup, values=constraints.qR, field_class=field_class)
        PqO = Polynomial.interpolate_poly(domain=mult_subgroup, values=constraints.qO, field_class=field_class)
        PqM = Polynomial.interpolate_poly(domain=mult_subgroup, values=constraints.qM, field_class=field_class)
        PqC = Polynomial.interpolate_poly(domain=mult_subgroup, values=constraints.qC, field_class=field_class)

        return PlonkPreprocessedInput(
            PqL=PqL,
            PqR=PqR,
            PqO=PqO,
            PqM=PqM,
            PqC=PqC,
            Sid1=s_id_polys[0],
            Sid2=s_id_polys[1],
            Sid3=s_id_polys[2],
            S1=s_sigma_polys[0],
            S2=s_sigma_polys[1],
            S3=s_sigma_polys[2]
        )

    @staticmethod
    def get_permutation_from_constraints(constraints: PlonkConstraints) -> List[int]:
        wiring_constraints = [constraints.a, constraints.b, constraints.c]
        wire_sets: List[List[int]] = [[]] * constraints.m
        for j in range(3):
            for i in range(constraints.n):
                value = wiring_constraints[j][i].n
                index = j * constraints.n + i
                wire_sets[value].append(index)

        res = [0] * (3 * constraints.n)
        for wire_set in wire_sets: 
            for i in range(len(wire_set)):
                res[wire_set[i]] = wire_set[(i + 1) % len(wire_set)]
        
        return res

