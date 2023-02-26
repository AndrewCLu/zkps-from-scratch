from dataclasses import dataclass
from typing import List, Generic
from algebra import FElt

@dataclass
class PlonkConstraints(Generic[FElt]):
    l: int # Number of public inputs
    m: int # Number of wires
    n: int # Number of gates
    a: List[FElt]
    b: List[FElt]
    c: List[FElt]
    qL: List[FElt]
    qR: List[FElt]
    qO: List[FElt]
    qM: List[FElt]
    qC: List[FElt]

    def is_valid_constraint(self) -> bool:
        # All lists must have length n
        if len(self.a) != self.n or \
            len(self.b) != self.n or \
            len(self.c) != self.n or \
            len(self.qL) != self.n or \
            len(self.qR) != self.n or \
            len(self.qO) != self.n or \
            len(self.qM) != self.n or \
            len(self.qC) != self.n:
            return False

        # Cannot have more public inputs than wires
        if self.l > self.m:
            return False
        
        # All values in wire constraints must lie between 1 and m
        for i in range(self.n):
            if self.a[i].n <= 0 or self.a[i].n > self.m or \
                self.b[i].n <= 0 or self.b[i].n > self.m or \
                self.c[i].n <= 0 or self.c[i].n > self.m:
                return False
        
        return True

    # This is a permutation from [0..3n-1] to itself based on the wiring of the gates
    def get_permutation(self) -> List[int]:
        wiring_constraints = [self.a, self.b, self.c]
        wire_sets: List[List[int]] = [[] for _ in range(self.m)]
        for j in range(3):
            for i in range(self.n):
                wire_index = wiring_constraints[j][i].n - 1 # Unique index of wire
                perm_index = j * self.n + i # Unique index of gate input/output
                wire_sets[wire_index].append(perm_index)

        res = [0] * (3 * self.n)
        for wire_set in wire_sets: 
            for i in range(len(wire_set)):
                res[wire_set[i]] = wire_set[(i + 1) % len(wire_set)]
        
        return res