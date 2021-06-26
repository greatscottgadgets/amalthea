from .complex import *

class TestComplex(unittest.TestCase):
    def check(self, v, expected):
        m = Module()
        sim = Simulator(m)
        def process():
            self.assertAlmostEqual((yield from v.to_complex()), expected, delta=0.01)

        sim.add_process(process)
        sim.run()

    def test_mul(self):
        for a,b,c,d in itertools.permutations([0,1,-1,0.5,-0.5],4):
            c1 = complex(a, b)
            c2 = complex(c, d)
            shape = Q(8,8)
            self.check((Complex(shape=shape, value=c1)*Complex(shape=shape, value=c2)), c1*c2)


if __name__ == "__main__":
    unittest.main()