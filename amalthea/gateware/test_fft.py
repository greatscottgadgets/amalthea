from .fft import *

class TestFFT(unittest.TestCase):
    def test_fft(self):
        clk = 60e6
        m = FFT(32, Q(1,10))

        input = [1+0j]*16 + [-1+0j]*16

        # Map input to Complex fixed-point
        data = list(map(lambda x: ComplexConst(m.internal_shape, x).value(), input))

        # Re-order with bit-reversed indices & write to FFT memory
        rev = lambda i: int('{:05b}'.format(i)[::-1], 2)
        m.mem.init = [data[rev(i)] for i in range(len(data))]

        sim = Simulator(m)
        sim.add_clock(1/clk)

        def process():
            yield m.start.eq(1)
            yield
            yield m.start.eq(0)
            yield

            while True:
                if ((yield m.done) == 1):
                    break
                yield

            expected = np.fft.fft(input)
            for i, sig in enumerate(m.mem._array):
                self.assertAlmostEqual(
                    (yield from Complex(shape=m.internal_shape, value=sig).to_complex()),
                    expected[i],
                    delta=0.02
                )


        sim.add_sync_process(process)
        with sim.write_vcd("fft.vcd", "fft.gtkw", traces=[]):
            sim.run()


class TestAddressGenerator(unittest.TestCase):
    def test_agu(self):
        clk = 60e6
        m = AddressGenerator(level_count=5, butterfly_count=16)

        sim = Simulator(m)
        sim.add_clock(1/clk)

        def process():
            expected_addrs = [
                (0,1), (2,3), (4,5), (6,7), (8,9), (10,11), (12,13), (14,15), (16,17), (18,19), (20,21), (22,23), (24,25), (26,27), (28,29), (30,31),
                (0,2), (4,6), (8,10), (12,14), (16,18), (20,22), (24,26), (28,30), (1,3), (5,7), (9,11), (13,15), (17,19), (21,23), (25,27), (29,31),
                (0,4), (8,12), (16,20), (24,28), (1,5), (9,13), (17,21), (25,29), (2,6), (10,14), (18,22), (26,30), (3,7), (11,15), (19,23), (27,31),
                (0,8), (16,24), (1,9), (17,25), (2,10), (18,26), (3,11), (19,27), (4,12), (20,28), (5,13), (21,29), (6,14), (22,30), (7,15), (23,31),
                (0,16), (1,17), (2,18), (3,19), (4,20), (5,21), (6,22), (7,23), (8,24), (9,25), (10,26), (11,27), (12,28), (13,29), (14,30), (15,31),
            ]
            for i in range(5):
                for j in range(16):
                    self.assertEqual(((yield m.addr_a), (yield m.addr_b)), expected_addrs[i*16+j])
                    self.assertEqual((yield m.addr_twiddle), ((0xfffffff0 >> i) & 0xf) & j)
                    yield

        sim.add_sync_process(process)
        with sim.write_vcd("agu.vcd", "agu.gtkw", traces=[]):
            sim.run()


class TestTwiddleFactors(unittest.TestCase):
    def test_tf(self):
        clk = 60e6
        m = TwiddleFactors(32, Q(1,15))

        # cast to unsigned
        real = Signal(16)
        imag = Signal(16)

        sim = Simulator(m)
        sim.add_clock(1/clk)

        def process():
            expected_tfs = [
                (0x7fff, 0x0000),
                (0x7d89, 0xe707),
                (0x7641, 0xcf05),
                (0x6a6d, 0xb8e4),
                (0x5a82, 0xa57e),
                (0x471c, 0x9593),
                (0x30fb, 0x89bf),
                (0x18f9, 0x8277),
                (0x0000, 0x8001),
                (0xe707, 0x8277),
                (0xcf05, 0x89bf),
                (0xb8e4, 0x9593),
                (0xa57e, 0xa57e),
                (0x9593, 0xb8e4),
                (0x89bf, 0xcf05),
                (0x8277, 0xe707),
            ]
            for i in range(16):
                yield m.addr.eq(i)
                yield
                yield
                yield real.eq(m.out.real.value)
                yield imag.eq(m.out.imag.value)
                yield
                self.assertEqual(((yield real), (yield imag)), expected_tfs[i])

        sim.add_sync_process(process)
        with sim.write_vcd("tf.vcd", "tf.gtkw", traces=[]):
            sim.run()


if __name__ == "__main__":
    unittest.main()