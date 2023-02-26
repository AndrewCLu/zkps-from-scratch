from plonk import PlonkProver, PlonkVerifier
from polynomial_commitment_schemes.trivial import TrivialProver, TrivialVerifier
from algebra import bn128_FR
from constraints import PlonkConstraints
from preprocessor import Preprocessor

def test_plonk_trivial_pcs():
    constraints = PlonkConstraints(
        l=3, 
        m=7, 
        n=3, 
        a=[bn128_FR(1), bn128_FR(3), bn128_FR(5)], 
        b=[bn128_FR(2), bn128_FR(4), bn128_FR(6)], 
        c=[bn128_FR(5), bn128_FR(6), bn128_FR(7)], 
        qL=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
        qR=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
        qO=[bn128_FR(-1), bn128_FR(-1), bn128_FR(-1)], 
        qM=[bn128_FR(0), bn128_FR(0), bn128_FR(0)], 
        qC=[bn128_FR(0), bn128_FR(0), bn128_FR(0)]
    )
    mult_subgroup = [bn128_FR(1), bn128_FR(2), bn128_FR(3)]
    field_class = bn128_FR
    preprocessed_input = Preprocessor.preprocess_plonk_constraints(constraints=constraints, mult_subgroup=mult_subgroup, field_class=field_class)

    pcs_prover = TrivialProver[bn128_FR]()
    pcs_verifier = TrivialVerifier[bn128_FR]()

    plonk_prover = PlonkProver[bn128_FR](pcs_prover=pcs_prover, constraints=constraints, preprocessed_input=preprocessed_input, mult_subgroup=mult_subgroup, field_class=field_class)
    plonk_verifier = PlonkVerifier[bn128_FR](pcs_verifier=pcs_verifier, preprocessed_input=preprocessed_input, mult_subgroup=mult_subgroup, field_class=field_class)

    public_inputs = [bn128_FR(10), bn128_FR(20), bn128_FR(30)]
    witness = public_inputs + [bn128_FR(40), bn128_FR(30), bn128_FR(70), bn128_FR(100)]

    proof = plonk_prover.prove(witness)
    valid_proof = plonk_verifier.verify(proof, public_inputs)
    assert(valid_proof == True)