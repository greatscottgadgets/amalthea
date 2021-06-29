
from amalthea.gateware.types.fixed_point import *

class TestFixedPoint(unittest.TestCase):
    def check(self, v, expected):
        m = Module()
        sim = Simulator(m)
        def process():
            self.assertAlmostEqual((yield from v.to_float()), expected, delta=0.01)

        sim.add_process(process)
        sim.run()

    def test_basic(self):
        self.check(Q(8,8).value(0.0), 0.0)
        self.check(Q(8,8).value(1.0), 1.0)
        self.check(Q(8,8).value(-1.0), -1.0)
        self.check(Q(8,8).value(1.5), 1.5)
        self.check(Q(8,8).value(-1.5), -1.5)

    def test_shape_errors(self):
        with self.assertRaises(TypeError):
            Q(8,8).value("test")

        with self.assertRaises(ValueError):
            Q(0,8, signed=True)

    def test_reshape(self):
        self.check(Q(8,8).value(3.14).reshape(Q(8,7)), 3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(9,8)), 3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(8,7)), -3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(9,8)), -3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(7,7)), 3.14)
        self.check(Q(8,8).value(3.14).reshape(Q(9,9)), 3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(7,7)), -3.14)
        self.check(Q(8,8).value(-3.14).reshape(Q(9,9)), -3.14)

    def test_add(self):
        tests = [
            (Q(8,8).value(1.2), Q(8,8).value(3.4), 4.6, Q(9,8)),
            (Q(8,8).value(1.2), Q(8,8).value(-3.4), -2.2, Q(9,8)),
        ]
        for a, b, r, s in tests:
            v = a + b
            self.check(v, r)
            self.assertEqual(v.shape, s)

    def test_add_max(self):
        v = Q(3,0).value(3.0) + Q(3,0).value(3.0)
        self.check(v, 6.0)
        self.assertEqual(v.shape, Q(4,0))

    def test_add_mixed_shapes(self):
        v = Q(8,0).value(3.0) + Q(1,7).value(0.125)
        self.check(v, 3.125)
        self.assertEqual(v.shape, Q(9,7))

    def test_sub(self):
        v = Q(8,8).value(1.2) + Q(8,8).value(-3.4)
        self.check(v, -2.2)
        self.assertEqual(v.shape, Q(9,8))

    def test_mul(self):
        v = Q(8,8).value(1.2) * Q(8,8).value(2)
        self.check(v, 2.4)
        self.assertEqual(v.shape, Q(16,16))


if __name__ == "__main__":
    unittest.main()