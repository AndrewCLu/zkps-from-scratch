from dataclasses import dataclass
from typing import List, Generic, Any, Type
from algebra import FElt, Polynomial
from constraints import PlonkConstraints
from preprocessor import PlonkPreprocessedInput
from polynomial_commitment_schemes.pcs import PCSProver, PCSVerifier, Commitment, Opening
from transcript import Transcript

@dataclass
class PlonkProof(Generic[FElt]):
    f_L_cm: Commitment
    f_R_cm: Commitment
    f_O_cm: Commitment
    z_cm: Commitment
    T_cm: Commitment
    eval_f_L: FElt
    eval_f_R: FElt
    eval_f_O: FElt
    eval_z: FElt
    eval_z_prime: FElt
    opening_f_L: Opening
    opening_f_R: Opening
    opening_f_O: Opening
    opening_z: Opening
    opening_z_prime: Opening

class PlonkProver(Generic[FElt]):
    # TODO: Maybe abstract mult_subgroup. There is a lot we assume about it here,
        # such as the fact that it is cyclic, its generator is the first element, etc. 
    def __init__(self, pcs_prover: PCSProver[FElt], constraints: PlonkConstraints[FElt], preprocessed_input: PlonkPreprocessedInput[FElt], mult_subgroup: List[FElt], field_class: Type[FElt]) -> None:
        if not constraints.is_valid_constraint():
            raise Exception("Constraints must be valid!")

        self.pcs_prover: PCSProver[FElt] = pcs_prover
        self.constraints: PlonkConstraints[FElt] = constraints
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
        self.mult_subgorup: List[FElt] = mult_subgroup
        self.field_class: Type[FElt] = field_class
        
    def prove(self, witness: List[FElt]) -> PlonkProof[FElt]:
        if len(witness) != self.constraints.m:
            raise Exception("Must have witness length equal to number of unique wires in constraints!")
        # TODO: Need check to make sure field size is greater than n or m

        transcript = Transcript[FElt](field_class=self.field_class)

        abc_constraints = [self.constraints.a, self.constraints.b, self.constraints.c]
        f_LRO_values: List[List[FElt]] = []
        f_polys: List[Polynomial[FElt]] = []
        f_cms: List[Commitment] = []
        for j in range(3):
            f_values = []
            for i in range(self.constraints.n):
                f_values.append(witness[abc_constraints[j][i].n])
            f_LRO_values.append(f_values)
            f_poly = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=f_values, field_class=self.field_class)
            f_polys.append(f_poly)
            f_cm = self.pcs_prover.commit(f_poly)
            f_cms.append(f_cm)
            
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
            f_poly = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=f_values, field_class=self.field_class)
            g_poly = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=g_values, field_class=self.field_class)
            f_prime_poly *= f_poly
            g_prime_poly *= g_poly
        # TODO: Move computation of z into above
        curr_prod = self.field_class.one()
        z_values: List[FElt] = [curr_prod]
        for i in range(self.constraints.n - 1):
            curr_prod *= f_prime_values[i] / g_prime_values[i]
            z_values.append(curr_prod)
        z_poly = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=z_values, field_class=self.field_class)
        z_cm = self.pcs_prover.commit(z_poly)

        transcript.append(z_cm.to_bytes())
        a_1 = transcript.get_hash(salt=bytes(0))
        a_2 = transcript.get_hash(salt=bytes(1))
        a_3 = transcript.get_hash(salt=bytes(2))

        L_1 = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=0, field_class=self.field_class)
        F_1 = L_1 * (z_poly - Polynomial[FElt](coeffs=[self.field_class.one()]))
        z_prime_values: List[FElt] = z_values[1:] + z_values[:1]
        z_prime_poly = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=z_prime_values, field_class=self.field_class)
        F_2 = z_poly * f_prime_poly - g_prime_poly * z_prime_poly
        PI_poly = Polynomial[FElt](coeffs=[self.field_class.zero()])
        for i in range(self.constraints.l):
            value = -witness[i]
            lagrange = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=i, field_class=self.field_class)
            PI_poly += lagrange * Polynomial[FElt](coeffs=[value])
        F_3 = self.preprocessed_input.PqL * f_polys[0] + \
            self.preprocessed_input.PqR * f_polys[1] + \
            self.preprocessed_input.PqO * f_polys[2] + \
            self.preprocessed_input.PqM * f_polys[0] * f_polys[1] + \
            self.preprocessed_input.PqC + PI_poly
        Z_S = Polynomial[FElt](coeffs=[self.field_class.one()])
        for i in range(len(self.mult_subgroup)):
            Z_S *= Polynomial[FElt](coeffs=[-self.mult_subgroup[i], self.field_class.one()])
        T_poly = (Polynomial[FElt](coeffs=[a_1]) * F_1 + \
            Polynomial[FElt](coeffs=[a_2]) * F_2 + \
            Polynomial[FElt](coeffs=[a_3]) * F_3) / Z_S
        T_cm = self.pcs_prover.commit(T_poly)

        transcript.append(T_cm.to_bytes())
        eval_chal = transcript.get_hash()

        eval_f_L = f_polys[0](eval_chal)
        eval_f_R = f_polys[1](eval_chal)
        eval_f_O = f_polys[2](eval_chal)
        eval_z = z_poly(eval_chal)
        eval_z_prime = z_prime_poly(eval_chal)

        transcript.append(eval_f_L.to_bytes())
        transcript.append(eval_f_R.to_bytes())
        transcript.append(eval_f_O.to_bytes())
        transcript.append(eval_z.to_bytes())
        transcript.append(eval_z_prime.to_bytes())

        open_chal = transcript.get_hash()
        opening_f_L = self.pcs_prover.open(f_polys[0], f_cms[0], eval_chal, eval_f_L, open_chal)
        opening_f_R = self.pcs_prover.open(f_polys[1], f_cms[1], eval_chal, eval_f_L, open_chal)
        opening_f_O = self.pcs_prover.open(f_polys[2], f_cms[2], eval_chal, eval_f_O, open_chal)
        opening_z = self.pcs_prover.open(z_poly, z_cm, eval_chal, eval_z, open_chal)
        # TODO: This is wrong, can't just evaluate z at g*x since z_prime is a totally different poly
        opening_z_prime = self.pcs_prover.open(z_poly, z_cm, self.mult_subgroup[0] * eval_chal, eval_z_prime, open_chal)

        transcript.append(opening_f_L)
        transcript.append(opening_f_R)
        transcript.append(opening_f_O)
        transcript.append(opening_z)
        transcript.append(opening_z_prime)

        return PlonkProof[FElt](
            f_L_cm = f_cms[0],
            f_R_cm = f_cms[1],
            f_O_cm = f_cms[2],
            z_cm = z_cm,
            T_cm = T_cm,
            eval_f_L = eval_f_L,
            eval_f_R = eval_f_R,
            eval_f_O = eval_f_O,
            eval_z = eval_z,
            eval_z_prime = eval_z_prime,
            opening_f_L = opening_f_L,
            opening_f_R = opening_f_R,
            opening_f_O = opening_f_O,
            opening_z = opening_z,
            opening_z_prime = opening_z_prime
        )



class PlonkVerifier(Generic[FElt]):
    def __init__(self, pcs_verifier: PCSVerifier[FElt], preprocessed_input: PlonkPreprocessedInput[FElt], mult_subgroup: List[FElt], field_class: Type[FElt]) -> None:
        self.pcs_verifier: PCSVerifier[FElt] = pcs_verifier
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
        self.mult_subgroup: List[FElt] = mult_subgroup
        self.field_class: Type[FElt] = field_class
    
    def verify(self, proof: PlonkProof[FElt], publicInputs: List[FElt]) -> bool:
        transcript = Transcript[FElt](field_class=self.field_class)
        transcript.append(proof.f_L_cm)
        transcript.append(proof.f_R_cm)
        transcript.append(proof.f_O_cm)
        alpha = transcript.get_hash(salt=bytes(0))
        beta = transcript.get_hash(salt=bytes(1))
        transcript.append(proof.z_cm)
        eval_chal = transcript.get_hash()
        transcript.append(proof.T_cm)
        open_chal = transcript.get_hash()
        
        # Check all pcs evaluations 
        # TODO: Batched evaluations
        self.pcs_verifier.verify_opening(op=proof.opening_f_L, cm=proof.f_L_cm, z=eval_chal, s=proof.eval_f_L, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.opening_f_R, cm=proof.f_R_cm, z=eval_chal, s=proof.eval_f_R, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.opening_f_O, cm=proof.f_O_cm, z=eval_chal, s=proof.eval_f_O, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.opening_z, cm=proof.z_cm, z=eval_chal, s=proof.eval_z, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.opening_z_prime, cm=proof.z_cm, z=(self.mult_subgroup[0] * eval_chal), s=proof.eval_z_prime, op_info=open_chal)

        # Check F1

        # Check F2

        # Check F3

        # Check quotient
