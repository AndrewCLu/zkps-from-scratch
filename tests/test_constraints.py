from constraints import PlonkConstraints
from algebra.field import bn128_FR

class TestConstraints():
    def test_valid_constraints(self):
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

        assert(constraints.is_valid_constraint())

    def test_invalid_length(self):
        constraints = PlonkConstraints(
            l=3,
            m=7,
            n=3,
            a=[bn128_FR(1), bn128_FR(3)],
            b=[bn128_FR(2), bn128_FR(4), bn128_FR(6)],
            c=[bn128_FR(5), bn128_FR(6), bn128_FR(7)],
            qL=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
            qR=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
            qO=[bn128_FR(-1), bn128_FR(-1), bn128_FR(-1)], 
            qM=[bn128_FR(0), bn128_FR(0), bn128_FR(0)], 
            qC=[bn128_FR(0), bn128_FR(0), bn128_FR(0)]
        )

        assert(not constraints.is_valid_constraint())
    
    def test_invalid_wires(self):
        constraints = PlonkConstraints(
            l=3,
            m=7,
            n=3,
            a=[bn128_FR(1), bn128_FR(3), bn128_FR(-1)],
            b=[bn128_FR(2), bn128_FR(4), bn128_FR(6)],
            c=[bn128_FR(5), bn128_FR(6), bn128_FR(7)],
            qL=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
            qR=[bn128_FR(1), bn128_FR(1), bn128_FR(1)], 
            qO=[bn128_FR(-1), bn128_FR(-1), bn128_FR(-1)], 
            qM=[bn128_FR(0), bn128_FR(0), bn128_FR(0)], 
            qC=[bn128_FR(0), bn128_FR(0), bn128_FR(0)]
        )

        assert(not constraints.is_valid_constraint())

    def test_permutation(self):
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

        expected = [0, 1, 6, 3, 4, 7, 2, 5, 8] # Note that permutations use 0-indexed notation
        assert(constraints.get_permutation() == expected)