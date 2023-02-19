from plonk import PlonkProver, PlonkVerifier
from polynomial_commitment_schemes.trivial import TrivialProver, TrivialVerifier
from algebra import bn128_FR
from constraints import PlonkConstraints
from preprocessor import preprocess_plonk_constraints

def test_plonk_sanity():
    contraints = PlonkConstraints(7, 3, [bn128_FR(1), bn128_FR(3), bn128_FR(5)], [bn128_FR(2), bn128_FR(4), bn128_FR(6)], [bn128_FR(5), bn128_FR(6), bn128_FR(7)], [bn128_FR(1), bn128_FR(1), bn128_FR(1)], [bn128_FR(1), bn128_FR(1), bn128_FR(1)], [bn128_FR(-1), bn128_FR(-1), bn128_FR(-1)], [bn128_FR(0), bn128_FR(0), bn128_FR(0)], [bn128_FR(0), bn128_FR(0), bn128_FR(0)])
    preprocessed_input = preprocess_plonk_constraints(contraints)

    pcs_prover = TrivialProver[bn128_FR]()
    pcs_verifier = TrivialVerifier[bn128_FR]()

    plonk_prover = PlonkProver[bn128_FR](pcs_prover, preprocessed_input)
    plonk_verifier = PlonkVerifier[bn128_FR](pcs_verifier, preprocessed_input)

    public_inputs = [bn128_FR(10), bn128_FR(20), bn128_FR(30)]
    witness = public_inputs + [bn128_FR(40), bn128_FR(30), bn128_FR(70), bn128_FR(100)]

    proof = plonk_prover.prove(witness)
    valid_proof = plonk_verifier.verify(proof, public_inputs)
    assert(valid_proof == True)