from polynomial_commitment_schemes.trivial import (
    TrivialProver,
    TrivialVerifier,
    TrivialOpening,
)
from algebra.field import bn128_FR
from algebra.polynomial import Polynomial


class TestTrivialPCS:
    prover = TrivialProver()
    verifier = TrivialVerifier()
    f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(2), bn128_FR(3)])
    z = bn128_FR(4)
    s = bn128_FR(57)
    cm = prover.commit(f=f)

    def test_commitment(self):
        assert self.cm.value == [bn128_FR(1), bn128_FR(2), bn128_FR(3)]

    # Openings are not used for the trivial commitment
    def test_correctness(self):
        assert self.verifier.verify_opening(
            op=TrivialOpening(value=None), cm=self.cm, z=self.z, s=self.s, op_info=None
        )

    def test_fails_on_bad_commit(self):
        g = Polynomial(coeffs=[bn128_FR(1), bn128_FR(2), bn128_FR(4)])
        cm_g = self.prover.commit(f=g)

        assert not self.verifier.verify_opening(
            op=TrivialOpening(value=None), cm=cm_g, z=self.z, s=self.s, op_info=None
        )

    def test_fails_on_bad_open_point(self):
        z_prime = bn128_FR(3)
        assert not self.verifier.verify_opening(
            op=TrivialOpening(value=None), cm=self.cm, z=z_prime, s=self.s, op_info=None
        )

    def test_fails_on_bad_open_value(self):
        s_prime = bn128_FR(59)
        assert not self.verifier.verify_opening(
            op=TrivialOpening(value=None), cm=self.cm, z=self.z, s=s_prime, op_info=None
        )
