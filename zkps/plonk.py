from dataclasses import dataclass
from typing import List, Generic, Any, Type
from algebra import FElt, Polynomial
from constraints import PlonkConstraints
from preprocessor import PlonkPreprocessedInput
from polynomial_commitment_schemes.pcs import PCSProver, PCSVerifier, Commitment
from transcript import Transcript

@dataclass
class PlonkProof(Generic[FElt]):
    a: Commitment
    b: Commitment
    
class PlonkProver(Generic[FElt]):
    def __init__(self, pcs_prover: PCSProver[FElt], constraints: PlonkConstraints[FElt], preprocessed_input: PlonkPreprocessedInput[FElt], field_class: Type[FElt]) -> None:
        if not constraints.is_valid_constraint():
            raise Exception("Constraints must be valid!")

        self.pcs_prover: PCSProver[FElt] = pcs_prover
        self.constraints: PlonkConstraints[FElt] = constraints
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
        self.field_class: Type[FElt] = field_class
        
    def prove(self, witness: List[FElt]) -> PlonkProof[FElt]:
        if len(witness) != self.constraints.m:
            raise Exception("Must have witness length equal to number of unique wires in constraints!")
        # TODO: Need check to make sure field size is greater than n or m

        mult_subgroup = self.field_class.get_roots_of_unity(self.constraints.n)
        transcript = Transcript()

        abc_constraints = [self.constraints.a, self.constraints.b, self.constraints.c]
        f_LRO_values: List[List[FElt]] = []
        for j in range(3):
            f_values = []
            for i in range(self.constraints.n):
                f_values.append(witness[abc_constraints[j][i].n])
            f_LRO_values.append(f_values)
            f_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=f_values, field_class=self.field_class)
            f_cm = self.pcs_prover.commit(f_poly)
            
            transcript.append(f_cm.to_bytes())

        beta = transcript.get_hash(salt=bytes(0))
        gamma = transcript.get_hash(salt=bytes(1))

        permutation = self.constraints.get_permutation()
        f_prime_values: List[FElt] = []
        g_prime_values: List[FElt] = []
        for j in range(3):
            for i in range(self.constraints.n):
                # TODO: Should add 1 to every identity and permutation index
                f_value = f_LRO_values[j][i] + beta * self.field_class(j * self.constraints.n + i) + gamma
                g_value = f_LRO_values[j][i] + beta * self.field_class(permutation[j * self.constraints.n + i]) + gamma
                if i >= len(f_prime_values):
                    f_prime_values.append(f_value)
                    g_prime_values.append(g_value)
                else:
                    f_prime_values[i] *= f_value
                    g_prime_values[i] *= g_value

        curr_prod = self.field_class.one()
        z_values: List[FElt] = [curr_prod]
        for i in range(self.constraints.n - 1):
            curr_prod *= f_prime_values[i] / g_prime_values[i]
            z_values.append(curr_prod)
        z_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=z_values, field_class=self.field_class)
        z_cm = self.pcs_prover.commit(z_poly)

        transcript.append(z_cm.to_bytes())
        
            

            
            




class PlonkVerifier(Generic[FElt]):
    def __init__(self, pcs_verifier: PCSVerifier[FElt], preprocessed_input: PlonkPreprocessedInput[FElt]) -> None:
        self.pcs_verifier: PCSVerifier[FElt] = pcs_verifier
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
    
    def verify(self, proof: PlonkProof[FElt], publicInputs: List[FElt]) -> bool:
        return self.pcs_verifier.verify_opening(proof.y, proof.x, publicInputs[0].one() * 2, publicInputs[0].one() * 15, None)