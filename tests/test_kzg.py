from polynomial_commitment_schemes.kzg import KZGProver, KZGVerifier, KZGSRS
from algebra import bn128, bn128_FR, Polynomial

class TestKZGPCS():
    field_class = bn128_FR
    ec = bn128
    srs = KZGSRS.trusted_setup(10, ec, field_class)
    prover = KZGProver(ec, srs)
    verifier = KZGVerifier(ec, srs)
    f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(2), bn128_FR(3)])
    z = bn128_FR(4)
    s = bn128_FR(57)
    cm = prover.commit(f=f)
    op = prover.open(f=f, cm=cm, z=z, s=s, op_info=None)

    def test_correctness(self):
        assert(self.verifier.verify_opening(op=self.op, cm=self.cm, z=self.z, s=self.s, op_info=None))
    
    def test_fails_on_bad_open_point(self):
        z_prime = bn128_FR(3)
        assert(not self.verifier.verify_opening(op=self.op, cm=self.cm, z=z_prime, s=self.s, op_info=None))

    def test_fails_on_bad_open_value(self):
        s_prime = bn128_FR(59)
        assert(not self.verifier.verify_opening(op=self.op, cm=self.cm, z=self.z, s=s_prime, op_info=None))
