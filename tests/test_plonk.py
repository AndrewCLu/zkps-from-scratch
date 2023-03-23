from plonk import PlonkProver, PlonkVerifier
from polynomial_commitment_schemes.trivial import TrivialProver, TrivialVerifier
from polynomial_commitment_schemes.kzg import KZGProver, KZGVerifier, KZGSRS
from polynomial_commitment_schemes.bulletproofs import BulletproofsCRS, BulletproofsProver, BulletproofsVerifier
from algebra.field import bn128_FR
from algebra.pairing import bn128, bn128_FQ_base, bn128_FQ2_base, bn128_FQ12_base
from algebra.cyclic_group import bn128Group
from constraints import PlonkConstraints
from preprocessor import Preprocessor

class TestPlonk():
    constraints = PlonkConstraints(
        l=2, 
        m=9, 
        n=4, 
        a=[bn128_FR(1), bn128_FR(3), bn128_FR(5), bn128_FR(8)], 
        b=[bn128_FR(2), bn128_FR(4), bn128_FR(6), bn128_FR(7)], 
        c=[bn128_FR(5), bn128_FR(7), bn128_FR(8), bn128_FR(9)], 
        qL=[bn128_FR(1), bn128_FR(1), bn128_FR(1), bn128_FR(0)], 
        qR=[bn128_FR(0), bn128_FR(0), bn128_FR(1), bn128_FR(0)], 
        qO=[bn128_FR(0), bn128_FR(0), bn128_FR(-1), bn128_FR(-1)], 
        qM=[bn128_FR(0), bn128_FR(0), bn128_FR(0), bn128_FR(1)], 
        qC=[bn128_FR(0), bn128_FR(0), bn128_FR(0), bn128_FR(0)]
    )
    mult_subgroup = bn128_FR.get_roots_of_unity(4)
    field_class = bn128_FR
    preprocessed_input = Preprocessor.preprocess_plonk_constraints(constraints=constraints, mult_subgroup=mult_subgroup, field_class=field_class)
    witness = [bn128_FR(10), bn128_FR(0), bn128_FR(20), bn128_FR(0), bn128_FR(10), bn128_FR(5), bn128_FR(20), bn128_FR(15), bn128_FR(300)]
    public_inputs = [bn128_FR(10), bn128_FR(20)]

    def test_plonk_trivial_pcs(self):
        pcs_prover = TrivialProver[bn128_FR]()
        pcs_verifier = TrivialVerifier[bn128_FR]()

        plonk_prover = PlonkProver[bn128_FR](pcs_prover=pcs_prover, constraints=self.constraints, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)
        plonk_verifier = PlonkVerifier[bn128_FR](pcs_verifier=pcs_verifier, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)

        proof = plonk_prover.prove(witness=self.witness, public_inputs=self.public_inputs)
        valid_proof = plonk_verifier.verify(proof=proof, public_inputs=self.public_inputs)
        assert(valid_proof == True)

    def test_plonk_kzg(self):
        ec = bn128()
        srs = KZGSRS.trusted_setup(d=10, ec=ec, field_class=self.field_class)
        pcs_prover = KZGProver[bn128_FR, bn128_FQ_base, bn128_FQ2_base, bn128_FQ12_base](ec=ec, srs=srs)
        pcs_verifier = KZGVerifier[bn128_FR, bn128_FQ_base, bn128_FQ2_base, bn128_FQ12_base](ec=ec, srs=srs)

        plonk_prover = PlonkProver[bn128_FR](pcs_prover=pcs_prover, constraints=self.constraints, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)
        plonk_verifier = PlonkVerifier[bn128_FR](pcs_verifier=pcs_verifier, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)

        proof = plonk_prover.prove(witness=self.witness, public_inputs=self.public_inputs)
        valid_proof = plonk_verifier.verify(proof=proof, public_inputs=self.public_inputs)
        assert(valid_proof == True)

    def test_plonk_bulletproofs(self):
        cyclic_group = bn128Group
        crs = BulletproofsCRS.common_setup(d=16, cyclic_group=cyclic_group)
        pcs_prover = BulletproofsProver(crs=crs, field_class=self.field_class)
        pcs_verifier = BulletproofsVerifier(crs=crs, field_class=self.field_class)

        plonk_prover = PlonkProver[bn128_FR](pcs_prover=pcs_prover, constraints=self.constraints, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)
        plonk_verifier = PlonkVerifier[bn128_FR](pcs_verifier=pcs_verifier, preprocessed_input=self.preprocessed_input, mult_subgroup=self.mult_subgroup, field_class=self.field_class)

        proof = plonk_prover.prove(witness=self.witness, public_inputs=self.public_inputs)
        valid_proof = plonk_verifier.verify(proof=proof, public_inputs=self.public_inputs)
        assert(valid_proof == True)