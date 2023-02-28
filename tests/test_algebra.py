from algebra import bn128_FR, Polynomial

class TestAdd:
    def test_add(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        g = Polynomial(coeffs=[bn128_FR(0), bn128_FR(0), bn128_FR(1), bn128_FR(3)])

        expected = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(4), bn128_FR(3), bn128_FR(40)])
        assert(f + g == expected)
    
    def test_truncation(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(40)])
        g = Polynomial(coeffs=[bn128_FR(0), bn128_FR(0), bn128_FR(-40)])

        expected = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1)])
        assert(f + g == expected)
    
class TestSub:
    def test_sub(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        g = Polynomial(coeffs=[bn128_FR(0), bn128_FR(0), bn128_FR(1), bn128_FR(3)])

        expected = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(2), bn128_FR(-3), bn128_FR(40)])
        assert(f - g == expected)

    def test_sub_longer_poly(self):
        f = Polynomial(coeffs=[bn128_FR(0), bn128_FR(0), bn128_FR(1), bn128_FR(3)])
        g = Polynomial(coeffs=[bn128_FR(4), bn128_FR(0), bn128_FR(1), bn128_FR(3), bn128_FR(10)])

        expected = Polynomial(coeffs=[bn128_FR(-4), bn128_FR(0), bn128_FR(0), bn128_FR(0), bn128_FR(-10)])
        assert(f - g == expected)
    
    def test_sub_scalar(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        g = bn128_FR(5)

        expected = Polynomial(coeffs=[bn128_FR(-4), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        assert(f - g == expected)

class TestMul:
    def test_mul(self):
        f = Polynomial(coeffs=[bn128_FR(6), bn128_FR(10), bn128_FR(1)])
        g = Polynomial(coeffs=[bn128_FR(2), bn128_FR(5)])

        expected = Polynomial(coeffs=[bn128_FR(12), bn128_FR(50), bn128_FR(52), bn128_FR(5)])
        assert(f * g == expected)

    def test_mul_scalar(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        c = bn128_FR(10)

        expected = Polynomial(coeffs=[bn128_FR(10), bn128_FR(10), bn128_FR(30), bn128_FR(0), bn128_FR(400)])
        assert(f * c == expected)

class TestDiv: 
    def test_div(self):
        f = Polynomial(coeffs=[bn128_FR(12), bn128_FR(50), bn128_FR(52), bn128_FR(5)])
        g = Polynomial(coeffs=[bn128_FR(2), bn128_FR(5)])

        expected_quo = Polynomial(coeffs=[bn128_FR(6), bn128_FR(10), bn128_FR(1)])
        expected_rem = Polynomial(coeffs=[bn128_FR(0)])
        assert(f / g == (expected_quo, expected_rem))

    def test_div_rem(self):
        f = Polynomial(coeffs=[bn128_FR(6), bn128_FR(1), bn128_FR(4), bn128_FR(5)])
        g = Polynomial(coeffs=[bn128_FR(1), bn128_FR(0), bn128_FR(1)])

        expected_quo = Polynomial(coeffs=[bn128_FR(4), bn128_FR(5)])
        expected_rem = Polynomial(coeffs=[bn128_FR(2), bn128_FR(-4)])
        assert(f / g == (expected_quo, expected_rem))

    def test_div_scalar(self):
        f = Polynomial(coeffs=[bn128_FR(10), bn128_FR(4), bn128_FR(0), bn128_FR(2)])
        c = bn128_FR(2)

        expected_quo = Polynomial(coeffs=[bn128_FR(5), bn128_FR(2), bn128_FR(0), bn128_FR(1)])
        expected_rem = Polynomial(coeffs=[bn128_FR(0)])
        assert(f / c == (expected_quo, expected_rem))
    
class TestEq:
    def test_eq(self):
        f = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])
        g = Polynomial(coeffs=[bn128_FR(1), bn128_FR(1), bn128_FR(3), bn128_FR(0), bn128_FR(40)])

        assert(f == g)

class TestLagrange:
    def test_lagrange_poly(self):
        domain = [bn128_FR(1), bn128_FR(2), bn128_FR(3), bn128_FR(4)]
        
        (expected, _) = Polynomial(coeffs=[bn128_FR(-8), bn128_FR(14), bn128_FR(-7), bn128_FR(1)]) / bn128_FR(-2)
        assert(Polynomial.lagrange_poly(domain=domain, index=2, field_class=bn128_FR) == expected)

class TestInterpolation:
    def test_interpolate_poly(self):
        domain = [bn128_FR(1), bn128_FR(2), bn128_FR(3)]
        values = [bn128_FR(6), bn128_FR(-1), bn128_FR(4)]

        expected = Polynomial(coeffs=[bn128_FR(25), bn128_FR(-25), bn128_FR(6)])
        assert(Polynomial.interpolate_poly(domain=domain, values=values, field_class=bn128_FR) == expected)
