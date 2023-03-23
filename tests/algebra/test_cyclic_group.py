from algebra.cyclic_group import bn128Group, bls12_381Group

class TestCyclicGroup:
    groups = [bn128Group, bls12_381Group]

    def test_add(self):
        for g in self.groups:
            a = g(100)
            b = g(200)

            c = g(300)
            assert (a + b == c)
        
    def test_mul(self):
        for g in self.groups:
            a = g(100)
            s = 10

            c = g(1000)
            assert (a * s == c)