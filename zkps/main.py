from plonk import PlonkProver, PlonkVerifier
from polynomial_commitment_schemes.trivial import TrivialProver, TrivialVerifier
from polynomial_commitment_schemes.kzg import KZGProver, KZGVerifier, KZGSRS
from polynomial_commitment_schemes.bulletproofs import BulletproofsProver, BulletproofsVerifier, BulletproofsCRS
from algebra.field import bn128_FR, bls12_381_FR
from algebra.cyclic_group import bn128_group, bls12_381_group
from algebra.pairing import bn128_pairing, bn128_FQ_base, bn128_FQ2_base, bn128_FQ12_base, bls12_381_pairing, bls12_381_FQ_base, bls12_381_FQ2_base, bls12_381_FQ12_base
from constraints import PlonkConstraints
from preprocessor import Preprocessor
from metrics import Counter

def run_plonk(field_class, pcs_prover, pcs_verifier):
    constraints = PlonkConstraints(
        l=2, 
        m=9, 
        n=4, 
        a=[field_class(1), field_class(3), field_class(5), field_class(8)], 
        b=[field_class(2), field_class(4), field_class(6), field_class(7)], 
        c=[field_class(5), field_class(7), field_class(8), field_class(9)], 
        qL=[field_class(1), field_class(1), field_class(1), field_class(0)], 
        qR=[field_class(0), field_class(0), field_class(1), field_class(0)], 
        qO=[field_class(0), field_class(0), field_class(-1), field_class(-1)], 
        qM=[field_class(0), field_class(0), field_class(0), field_class(1)], 
        qC=[field_class(0), field_class(0), field_class(0), field_class(0)]
    )
    mult_subgroup = field_class.get_roots_of_unity(4)
    preprocessed_input = Preprocessor.preprocess_plonk_constraints(constraints=constraints, mult_subgroup=mult_subgroup, field_class=field_class)
    witness = [field_class(10), field_class(0), field_class(20), field_class(0), field_class(10), field_class(5), field_class(20), field_class(15), field_class(300)]
    public_inputs = [field_class(10), field_class(20)]

    plonk_prover = PlonkProver(pcs_prover=pcs_prover, constraints=constraints, preprocessed_input=preprocessed_input, mult_subgroup=mult_subgroup, field_class=field_class)
    plonk_verifier = PlonkVerifier(pcs_verifier=pcs_verifier, preprocessed_input=preprocessed_input, mult_subgroup=mult_subgroup, field_class=field_class)
    proof = plonk_prover.prove(witness=witness, public_inputs=public_inputs)
    valid_proof = plonk_verifier.verify(proof=proof, public_inputs=public_inputs)
    return valid_proof

def main():
    for field_class in [bn128_FR, bls12_381_FR]:
        pcs_prover = TrivialProver()
        pcs_verifier = TrivialVerifier()
        print("---------- START RUNNING PLONK WITH {field_class_name} + TRIVIAL PCS ----------".format(field_class_name=field_class.__name__))
        valid_proof = run_plonk(field_class, pcs_prover, pcs_verifier)
        print("Valid proof: {}".format(valid_proof))
        Counter.display()
        Counter.reset()
        print("---------- END RUNNING PLONK WITH {field_class_name} + TRIVIAL PCS ----------\n\n".format(field_class_name=field_class.__name__))

        pairing = bn128_pairing() if field_class == bn128_FR else bls12_381_pairing()
        srs = KZGSRS.trusted_setup(d=10, pairing=pairing, field_class=field_class)
        pcs_prover = KZGProver(srs=srs, pairing=pairing, field_class=field_class)
        pcs_verifier = KZGVerifier(srs=srs, pairing=pairing, field_class=field_class)
        print("---------- START RUNNING PLONK WITH {field_class_name} + KZG PCS ----------".format(field_class_name=field_class.__name__))
        valid_proof = run_plonk(field_class, pcs_prover, pcs_verifier)
        print("Valid proof: {}".format(valid_proof))
        Counter.display()
        Counter.reset()
        print("---------- END RUNNING PLONK WITH {field_class_name} + KZG PCS ----------\n\n".format(field_class_name=field_class.__name__))

        cyclic_group_class = bn128_group if field_class == bn128_FR else bls12_381_group
        crs = BulletproofsCRS.common_setup(d=16, cyclic_group_class=cyclic_group_class)
        pcs_prover = BulletproofsProver(crs=crs, field_class=field_class, cyclic_group_class=cyclic_group_class)
        pcs_verifier = BulletproofsVerifier(crs=crs, field_class=field_class, cyclic_group_class=cyclic_group_class)
        print("---------- START RUNNING PLONK WITH {field_class_name} + BULLETPROOFS PCS ----------".format(field_class_name=field_class.__name__))
        valid_proof = run_plonk(field_class, pcs_prover, pcs_verifier)
        print("Valid proof: {}".format(valid_proof))
        Counter.display()
        Counter.reset()
        print("---------- END RUNNING PLONK WITH {field_class_name} + BULLETPROOFS PCS ----------\n\n".format(field_class_name=field_class.__name__))

if __name__ == "__main__":
    main()