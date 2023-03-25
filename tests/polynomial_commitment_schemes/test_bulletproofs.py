from polynomial_commitment_schemes.bulletproofs import BulletproofsProver, BulletproofsVerifier, BulletproofsCRS
from algebra.field import bn128_FR
from algebra.polynomial import Polynomial
from algebra.cyclic_group import bn128_group

class TestBulletproofsPCS():
    field_class = bn128_FR
    cyclic_group_class = bn128_group
    crs = BulletproofsCRS.common_setup(10, cyclic_group_class)
    prover = BulletproofsProver(crs, field_class, cyclic_group_class)
    verifier = BulletproofsVerifier(crs, field_class, cyclic_group_class)
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
