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
        
    def prove(self, witness: List[FElt], num_public_inputs: int) -> PlonkProof[FElt]:
        if len(witness) != self.constraints.m:
            raise Exception("Must have witness length equal to number of unique wires in constraints!")
        if num_public_inputs > len(witness):
            raise Exception("Cannot have more public inputs than number of wires!")
        # TODO: Need check to make sure field size is greater than n or m

        # TODO: Maybe abstract mult_subgroup. There is a lot we assume about it here,
        # such as the fact that it is cyclic, its generator is the first element, etc. 
        mult_subgroup = self.field_class.get_roots_of_unity(self.constraints.n)
        transcript = Transcript(field_class=self.field_class)

        abc_constraints = [self.constraints.a, self.constraints.b, self.constraints.c]
        f_LRO_values: List[List[FElt]] = []
        f_polys: List[Polynomial[FElt]] = []
        for j in range(3):
            f_values = []
            for i in range(self.constraints.n):
                f_values.append(witness[abc_constraints[j][i].n])
            f_LRO_values.append(f_values)
            f_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=f_values, field_class=self.field_class)
            f_polys.append(f_poly)
            f_cm = self.pcs_prover.commit(f_poly)
            
            transcript.append(f_cm.to_bytes())

        beta = transcript.get_hash(salt=bytes(0))
        gamma = transcript.get_hash(salt=bytes(1))

        permutation = self.constraints.get_permutation()
        # f_prime_values and g_prime_values are purely used to make it easier to calculate z, 
        # since it is defined by its values on the multiplicative subgroup
        # To compute f_prime_poly and g_prime_poly, we need to multiply the individual
        # f's and g's together, or know their values on a domain of size 3n rather than n
        f_prime_values: List[FElt] = []
        g_prime_values: List[FElt] = []
        f_prime_poly: Polynomial[FElt] = Polynomial[FElt](coeffs=[self.field_class.one()])
        g_prime_poly: Polynomial[FElt] = Polynomial[FElt](coeffs=[self.field_class.one()])
        for j in range(3):
            f_values: List[FElt] = []
            g_values: List[FElt] = []
            for i in range(self.constraints.n):
                # TODO: Should add 1 to every identity and permutation index
                f_value = f_LRO_values[j][i] + beta * self.field_class(j * self.constraints.n + i) + gamma
                g_value = f_LRO_values[j][i] + beta * self.field_class(permutation[j * self.constraints.n + i]) + gamma
                f_values.append(f_value)
                g_values.append(g_value)
                if i >= len(f_prime_values):
                    f_prime_values.append(f_value)
                    g_prime_values.append(g_value)
                else:
                    f_prime_values[i] *= f_value
                    g_prime_values[i] *= g_value
            f_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=f_values, field_class=self.field_class)
            g_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=g_values, field_class=self.field_class)
            f_prime_poly *= f_poly
            g_prime_poly *= g_poly
        # TODO: Move computation of z into above
        curr_prod = self.field_class.one()
        z_values: List[FElt] = [curr_prod]
        for i in range(self.constraints.n - 1):
            curr_prod *= f_prime_values[i] / g_prime_values[i]
            z_values.append(curr_prod)
        z_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=z_values, field_class=self.field_class)
        z_cm = self.pcs_prover.commit(z_poly)

        transcript.append(z_cm.to_bytes())
        a_1 = transcript.get_hash(salt=bytes(0))
        a_2 = transcript.get_hash(salt=bytes(1))
        a_3 = transcript.get_hash(salt=bytes(2))

        L_1 = Polynomial.lagrange_poly(domain=mult_subgroup, index=0, field_class=self.field_class)
        F_1 = L_1 * (z_poly - Polynomial[FElt](coeffs=[self.field_class.one()]))
        z_prime_values: List[FElt] = z_values[1:] + z_values[:1]
        z_prime_poly = Polynomial.interpolate_poly(domain=mult_subgroup, values=z_prime_values, field_class=self.field_class)
        F_2 = z_poly * f_prime_poly - g_prime_poly * z_prime_poly
        PI_poly = Polynomial[FElt](coeffs=[self.field_class.zero()])
        for i in range(num_public_inputs):
            value = -witness[i]
            lagrange = Polynomial.lagrange_poly(domain=mult_subgroup, index=i, field_class=self.field_class)
            PI_poly += lagrange * Polynomial[FElt](coeffs=[value])
        F_3 = self.preprocessed_input.PqL * f_polys[0] + \
            self.preprocessed_input.PqR * f_polys[1] + \
            self.preprocessed_input.PqO * f_polys[2] + \
            self.preprocessed_input.PqM * f_polys[0] * f_polys[1] + \
            self.preprocessed_input.PqC + PI_poly
        Z_S = Polynomial[FElt](coeffs=[self.field_class.one()])
        for i in range(len(mult_subgroup)):
            Z_S *= Polynomial[FElt](coeffs=[-mult_subgroup[i], self.field_class.one()])
        T_poly = (Polynomial[FElt](coeffs=[a_1]) * F_1 + \
            Polynomial[FElt](coeffs=[a_2]) * F_2 + \
            Polynomial[FElt](coeffs=[a_3]) * F_3) / Z_S
        T_cm = self.pcs_prover.commit(T_poly)

        transcript.append(T_cm.to_bytes())
            

            
            




class PlonkVerifier(Generic[FElt]):
    def __init__(self, pcs_verifier: PCSVerifier[FElt], preprocessed_input: PlonkPreprocessedInput[FElt]) -> None:
        self.pcs_verifier: PCSVerifier[FElt] = pcs_verifier
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
    
    def verify(self, proof: PlonkProof[FElt], publicInputs: List[FElt]) -> bool:
        return self.pcs_verifier.verify_opening(proof.y, proof.x, publicInputs[0].one() * 2, publicInputs[0].one() * 15, None)