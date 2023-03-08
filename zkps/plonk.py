from dataclasses import dataclass
from typing import List, Generic, Any, Type
from algebra import FElt, Polynomial
from constraints import PlonkConstraints
from preprocessor import PlonkPreprocessedInput
from polynomial_commitment_schemes.pcs import PCSProver, PCSVerifier, Commitment, Opening
from transcript import Transcript
from copy import deepcopy

@dataclass
class PlonkProof(Generic[FElt]):
    f_L_cm: Commitment
    f_R_cm: Commitment
    f_O_cm: Commitment
    Z_cm: Commitment
    Z_shift_cm: Commitment
    T_cm: Commitment
    f_L_eval: FElt
    f_R_eval: FElt
    f_O_eval: FElt
    Z_eval: FElt
    Z_shift_eval: FElt
    T_eval: FElt
    f_L_op: Opening
    f_R_op: Opening
    f_O_op: Opening
    Z_op: Opening
    Z_shift_op: Opening
    T_op: Opening

class PlonkProver(Generic[FElt]):
    def __init__(self, pcs_prover: PCSProver[FElt], constraints: PlonkConstraints[FElt], preprocessed_input: PlonkPreprocessedInput[FElt], mult_subgroup: List[FElt], field_class: Type[FElt]) -> None:
        if not constraints.is_valid_constraint():
            raise Exception("Constraints must be valid!")
        if not field_class.field_modulus > 3 * constraints.n:
            raise Exception("Field size must be greater than total number of wire variables!")

        self.pcs_prover: PCSProver[FElt] = pcs_prover
        self.constraints: PlonkConstraints[FElt] = constraints
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
        self.mult_subgroup: List[FElt] = mult_subgroup
        self.field_class: Type[FElt] = field_class
        
    def prove(self, witness: List[FElt], public_inputs: List[FElt]) -> PlonkProof[FElt]:
        if len(witness) != self.constraints.m:
            raise Exception("Must have witness length equal to number of unique wires in constraints!")
        if len(public_inputs) != self.constraints.l:
            raise Exception("Must have public input length equal to number of public inputs in constraints!")

        transcript = Transcript[FElt](field_class=self.field_class)

        # ---------- Commit to f_L, f_R, f_O ----------
        f_L_values = [witness[self.constraints.a[i].n - 1] for i in range(self.constraints.n)]
        f_L = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=f_L_values, field_class=self.field_class)
        f_L_cm = self.pcs_prover.commit(f_L)
        f_R_values = [witness[self.constraints.b[i].n - 1] for i in range(self.constraints.n)]
        f_R = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=f_R_values, field_class=self.field_class)
        f_R_cm = self.pcs_prover.commit(f_R)
        f_O_values = [witness[self.constraints.c[i].n - 1] for i in range(self.constraints.n)]
        f_O = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=f_O_values, field_class=self.field_class)
        f_O_cm = self.pcs_prover.commit(f_O)
        transcript.append(f_L_cm)
        transcript.append(f_R_cm)
        transcript.append(f_O_cm)

        # ---------- Commit to grand product polynomial Z ----------
        beta = transcript.get_hash(salt=bytes(0))
        gamma = transcript.get_hash(salt=bytes(1))
        f_prime_1 = f_L + self.preprocessed_input.Sid1 * beta + Polynomial[FElt](coeffs=[gamma])
        g_prime_1 = f_L + self.preprocessed_input.S1 * beta + Polynomial[FElt](coeffs=[gamma])
        f_prime_2 = f_R + self.preprocessed_input.Sid2 * beta + Polynomial[FElt](coeffs=[gamma])
        g_prime_2 = f_R + self.preprocessed_input.S2 * beta + Polynomial[FElt](coeffs=[gamma])
        f_prime_3 = f_O + self.preprocessed_input.Sid3 * beta + Polynomial[FElt](coeffs=[gamma])
        g_prime_3 = f_O + self.preprocessed_input.S3 * beta + Polynomial[FElt](coeffs=[gamma])
        f_prime = f_prime_1 * f_prime_2 * f_prime_3
        g_prime = g_prime_1 * g_prime_2 * g_prime_3
        Z_values = [self.field_class.one()]
        prod = self.field_class.one()
        for i in range(self.constraints.n - 1):
            prod *= f_prime(self.mult_subgroup[i]) / g_prime(self.mult_subgroup[i])
            Z_values.append(self.field_class(prod.n)) # Copy over product value into new field element
        Z = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=Z_values, field_class=self.field_class)
        Z_cm = self.pcs_prover.commit(Z)
        Z_shift_values = deepcopy(Z_values[1:] + Z_values[:1]) # Represents values of Z(a*g)
        Z_shift = Polynomial.interpolate_poly(domain=self.mult_subgroup, values=Z_shift_values, field_class=self.field_class)
        Z_shift_cm = self.pcs_prover.commit(Z_shift)
        transcript.append(Z_cm)
        transcript.append(Z_shift_cm)

        # ---------- Commit to quotient polynomial T ----------
        a_1 = transcript.get_hash(salt=bytes(0))
        a_2 = transcript.get_hash(salt=bytes(1))
        a_3 = transcript.get_hash(salt=bytes(2))
        L_1 = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=0, field_class=self.field_class)
        F_1 = L_1 * (Z - self.field_class.one())
        F_2 = Z * f_prime - g_prime * Z_shift
        PI = Polynomial[FElt](coeffs=[self.field_class.zero()])
        for i in range(self.constraints.l):
            lagrange = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=i, field_class=self.field_class)
            PI += lagrange * -public_inputs[i]
        F_3 = self.preprocessed_input.PqL * f_L + \
            self.preprocessed_input.PqR * f_R + \
            self.preprocessed_input.PqO * f_O + \
            self.preprocessed_input.PqM * f_L * f_R + \
            self.preprocessed_input.PqC + PI

        # ---------- Begin logging... ----------
        # for i in range(len(self.mult_subgroup)):
        #     print('F_1({}) = {}'.format(i, F_1(self.mult_subgroup[i])))
        #     print('F_2({}) = {}'.format(i, F_2(self.mult_subgroup[i])))
        #     print('F_3({}) = {}'.format(i, F_3(self.mult_subgroup[i])))
        #     print('f_L({}) = {}'.format(i, f_L(self.mult_subgroup[i])))
        #     print('f_R({}) = {}'.format(i, f_R(self.mult_subgroup[i])))
        #     print('f_O({}) = {}'.format(i, f_O(self.mult_subgroup[i])))
        #     print('q_L({}) = {}'.format(i, self.preprocessed_input.PqL(self.mult_subgroup[i])))
        #     print('q_R({}) = {}'.format(i, self.preprocessed_input.PqR(self.mult_subgroup[i])))
        #     print('q_O({}) = {}'.format(i, self.preprocessed_input.PqO(self.mult_subgroup[i])))
        #     print('q_M({}) = {}'.format(i, self.preprocessed_input.PqM(self.mult_subgroup[i])))
        #     print('q_C({}) = {}'.format(i, self.preprocessed_input.PqC(self.mult_subgroup[i])))
        #     print('PI({}) = {}'.format(i, PI(self.mult_subgroup[i])))
        # ---------- End logging... ----------

        Z_S = Polynomial[FElt](coeffs=[self.field_class.one()])
        for i in range(len(self.mult_subgroup)):
            Z_S *= Polynomial[FElt](coeffs=[-self.mult_subgroup[i], self.field_class.one()])
        T, T_rem = (Polynomial[FElt](coeffs=[a_1]) * F_1 + \
            Polynomial[FElt](coeffs=[a_2]) * F_2 + \
            Polynomial[FElt](coeffs=[a_3]) * F_3) / Z_S
        # If prover is honest Z_S divides cleanly
        if T_rem != Polynomial[FElt](coeffs=[self.field_class.zero()]):
            raise Exception("Unable to compute T polynomial: Z_S does not divide evenly!")
        T_cm = self.pcs_prover.commit(T)
        transcript.append(T_cm)

        # ---------- Compute evaluations of all polynomials ----------
        eval_chal = transcript.get_hash()
        f_L_eval = f_L(eval_chal)
        f_R_eval = f_R(eval_chal)
        f_O_eval = f_O(eval_chal)
        Z_eval = Z(eval_chal)
        Z_shift_eval = Z_shift(eval_chal)
        T_eval = T(eval_chal)
        transcript.append(f_L_eval)
        transcript.append(f_R_eval)
        transcript.append(f_O_eval)
        transcript.append(Z_eval)
        transcript.append(Z_shift_eval)
        transcript.append(T_eval)  

        # ---------- Compute opening proofs of all commitments ----------
        open_chal = transcript.get_hash()
        f_L_op = self.pcs_prover.open(f=f_L, cm=f_L_cm, z=eval_chal, s=f_L_eval, op_info=open_chal)
        f_R_op = self.pcs_prover.open(f=f_R, cm=f_R_cm, z=eval_chal, s=f_R_eval, op_info=open_chal)
        f_O_op = self.pcs_prover.open(f=f_O, cm=f_O_cm, z=eval_chal, s=f_O_eval, op_info=open_chal)
        Z_op = self.pcs_prover.open(f=Z, cm=Z_cm, z=eval_chal, s=Z_eval, op_info=open_chal)
        Z_shift_op = self.pcs_prover.open(f=Z_shift, cm=Z_shift_cm, z=eval_chal, s=Z_shift_eval, op_info=open_chal)
        T_op = self.pcs_prover.open(f=T, cm=T_cm, z=eval_chal, s=T_eval, op_info=open_chal)

        return PlonkProof[FElt](
            f_L_cm=f_L_cm,
            f_R_cm=f_R_cm,
            f_O_cm=f_O_cm,
            Z_cm=Z_cm,
            Z_shift_cm=Z_shift_cm,
            T_cm=T_cm,
            f_L_eval=f_L_eval,
            f_R_eval=f_R_eval,
            f_O_eval=f_O_eval,
            Z_eval=Z_eval,
            Z_shift_eval=Z_shift_eval,
            T_eval=T_eval,
            f_L_op=f_L_op,
            f_R_op=f_R_op,
            f_O_op=f_O_op,
            Z_op=Z_op,
            Z_shift_op=Z_shift_op,
            T_op=T_op
        )



class PlonkVerifier(Generic[FElt]):
    def __init__(self, pcs_verifier: PCSVerifier[FElt], preprocessed_input: PlonkPreprocessedInput[FElt], mult_subgroup: List[FElt], field_class: Type[FElt]) -> None:
        self.pcs_verifier: PCSVerifier[FElt] = pcs_verifier
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
        self.mult_subgroup: List[FElt] = mult_subgroup
        self.field_class: Type[FElt] = field_class
    
    def verify(self, proof: PlonkProof[FElt], public_inputs: List[FElt]) -> bool:
        # ---------- Re-execute transcript based on proof values ----------
        transcript = Transcript[FElt](field_class=self.field_class)
        transcript.append(proof.f_L_cm)
        transcript.append(proof.f_R_cm)
        transcript.append(proof.f_O_cm)
        beta = transcript.get_hash(salt=bytes(0))
        gamma = transcript.get_hash(salt=bytes(1))
        transcript.append(proof.Z_cm)
        transcript.append(proof.Z_shift_cm)
        a_1 = transcript.get_hash(salt=bytes(0))
        a_2 = transcript.get_hash(salt=bytes(1))
        a_3 = transcript.get_hash(salt=bytes(2))
        transcript.append(proof.T_cm)
        eval_chal = transcript.get_hash()
        transcript.append(proof.f_L_eval)
        transcript.append(proof.f_R_eval)
        transcript.append(proof.f_O_eval)
        transcript.append(proof.Z_eval)
        transcript.append(proof.Z_shift_eval)
        transcript.append(proof.T_eval)
        open_chal = transcript.get_hash()
        
        # ---------- Verify all polynomial commitments ----------
        # TODO: Batched evaluations
        # TODO: Fail if any of these verification openings fail
        self.pcs_verifier.verify_opening(op=proof.f_L_op, cm=proof.f_L_cm, z=eval_chal, s=proof.f_L_eval, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.f_R_op, cm=proof.f_R_cm, z=eval_chal, s=proof.f_R_eval, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.f_O_op, cm=proof.f_O_cm, z=eval_chal, s=proof.f_O_eval, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.Z_op, cm=proof.Z_cm, z=eval_chal, s=proof.Z_eval, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.Z_shift_op, cm=proof.Z_shift_cm, z=eval_chal, s=proof.Z_shift_eval, op_info=open_chal)
        self.pcs_verifier.verify_opening(op=proof.T_op, cm=proof.T_cm, z = eval_chal, s=proof.T_eval, op_info=open_chal)

        # ---------- Compute evaulation of F_1 ----------
        L_1 = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=0, field_class=self.field_class)
        F_1_eval = L_1(eval_chal) * (proof.Z_eval - self.field_class.one())

        # ---------- Compute evaulation of F_2 ----------
        f_prime_eval = (proof.f_L_eval + beta * self.preprocessed_input.Sid1(eval_chal) + gamma) * \
            (proof.f_R_eval + beta * self.preprocessed_input.Sid2(eval_chal) + gamma) * \
            (proof.f_O_eval + beta * self.preprocessed_input.Sid3(eval_chal) + gamma) 
        g_prime_eval = (proof.f_L_eval + beta * self.preprocessed_input.S1(eval_chal) + gamma) * \
            (proof.f_R_eval + beta * self.preprocessed_input.S2(eval_chal) + gamma) * \
            (proof.f_O_eval + beta * self.preprocessed_input.S3(eval_chal) + gamma) 
        F_2_eval = proof.Z_eval * f_prime_eval - g_prime_eval * proof.Z_shift_eval

        # ---------- Compute evaulation of F_3 ----------
        PI = Polynomial[FElt](coeffs=[self.field_class.zero()])
        for i in range(len(public_inputs)):
            lagrange = Polynomial.lagrange_poly(domain=self.mult_subgroup, index=i, field_class=self.field_class)
            PI += lagrange * -public_inputs[i]
        F_3_eval = self.preprocessed_input.PqL(eval_chal) * proof.f_L_eval + \
            self.preprocessed_input.PqR(eval_chal) * proof.f_R_eval + \
            self.preprocessed_input.PqO(eval_chal) * proof.f_O_eval + \
            self.preprocessed_input.PqM(eval_chal) * proof.f_L_eval * proof.f_R_eval + \
            self.preprocessed_input.PqC(eval_chal) + PI(eval_chal)

        # ---------- Compute evaulation of divisor polynomial Z_S ----------
        Z_S = Polynomial[FElt](coeffs=[self.field_class.one()])
        for i in range(len(self.mult_subgroup)):
            Z_S *= Polynomial[FElt](coeffs=[-self.mult_subgroup[i], self.field_class.one()])
        Z_S_eval = Z_S(eval_chal)

        # ---------- Verify quotient identity ----------
        return (a_1 * F_1_eval + a_2 * F_2_eval + a_3 * F_3_eval - proof.T_eval * Z_S_eval) == self.field_class.zero()















