from nmigen import *
from nmigen.hdl.dsl import _ModuleBuilderSubmodules
from nmigen.sim import Simulator, Settle
from .types.complex import Complex, ComplexConst
from .types.fixed_point import Q
from .util import variable_rotate_left
import cmath
import math
import numpy as np
import unittest

class FFT(Elaboratable):
    def __init__(self, fft_size, sample_shape):
        self.fft_size = fft_size
        levels = math.log2(fft_size)
        assert levels.is_integer()
        self.level_count = int(levels)
        self.butterfly_count = int(fft_size / 2)

        self.sample_shape = sample_shape
        self.internal_shape = Q(sample_shape.integer_bits + self.level_count, sample_shape.fraction_bits)
        self.twiddle_factor_shape = Q(1, len(self.internal_shape)-1)

        self.mem = Memory(width=len(Complex(shape=self.internal_shape).value()), depth=fft_size)
        self.read_addr = Signal(range(fft_size))
        self.read_data = Signal(self.mem.width)

        self.start = Signal()
        self.done = Signal()

        self._addr_gen = AddressGenerator(self.level_count, self.butterfly_count)
        self._butterfly = Butterfly(self.internal_shape, self.twiddle_factor_shape)

    def elaborate(self, platform):
        m = Module()

        next_address = Signal()
        reset = Signal()

        m.submodules.addr_gen = ResetInserter(reset)(
            EnableInserter(next_address)(
                self._addr_gen
            )
        )

        m.submodules.butterfly = self._butterfly
        m.submodules.twiddle_factors = twiddle_factors = TwiddleFactors(self.fft_size, self.twiddle_factor_shape)

        m.submodules.read_a = read_a = self.mem.read_port(transparent=False)
        m.submodules.read_b = read_b = self.mem.read_port(transparent=False)
        m.submodules.write_a = write_a = self.mem.write_port()
        m.submodules.write_b = write_b = self.mem.write_port()
        m.d.comb += [
            # Addresses
            read_a.addr.eq(Mux(self.done, self.read_addr, self._addr_gen.addr_a)),
            read_b.addr.eq(self._addr_gen.addr_b),
            write_a.addr.eq(self._addr_gen.addr_a),
            write_b.addr.eq(self._addr_gen.addr_b),
            twiddle_factors.addr.eq(self._addr_gen.addr_twiddle),

            # Data reads
            self._butterfly.in_a.value().eq(read_a.data),
            self._butterfly.in_b.value().eq(read_b.data),
            self._butterfly.twiddle_factor.eq(twiddle_factors.out),
            self.read_data.eq(read_a.data),

            # Data writes
            write_a.data.eq(self._butterfly.out_a.value()),
            write_b.data.eq(self._butterfly.out_b.value()),
        ]
        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.comb += [
                    reset.eq(1),
                    self.done.eq(1),
                ]
                with m.If(self.start):
                    m.next = "READ"

            with m.State("READ"):
                m.d.comb += [
                    read_a.en.eq(1),
                    read_b.en.eq(1),
                ]
                m.next = "WAIT"
                with m.If(self._addr_gen.done):
                    m.next = "IDLE"

            with m.State("WAIT"):
                m.next = "WRITE"

            with m.State("WRITE"):
                m.d.comb += [
                    write_a.en.eq(1),
                    write_b.en.eq(1),
                    next_address.eq(1),
                ]
                m.next = "READ"


        return m


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


class AddressGenerator(Elaboratable):
    def __init__(self, level_count, butterfly_count):
        self.level_count = level_count
        self.butterfly_count = butterfly_count

        self.done         = Signal()
        self.addr_a       = Signal(range(butterfly_count*2))
        self.addr_b       = Signal(range(butterfly_count*2))
        self.addr_twiddle = Signal(range(butterfly_count))

    def elaborate(self, platform):
        m = Module()

        level        = Signal(range(self.level_count))
        index        = Signal(range(self.butterfly_count))
        twiddle_mask = Signal.like(index)

        final_level = (level == self.level_count - 1)
        next_level  = (index == self.butterfly_count - 1)


        with m.If(next_level):
            m.d.sync += [
                level.eq(level + 1),
                index.eq(0),
                twiddle_mask.eq(Cat(twiddle_mask[1:], 1)),
            ]
            with m.If(final_level):
                m.d.sync += self.done.eq(1)

        with m.Else():
            m.d.sync += [
                index.eq(index + 1),
            ]

        addr_a = (index << 1)
        addr_b = addr_a + 1

        addr_a = variable_rotate_left(addr_a[:self.level_count], level)
        addr_b = variable_rotate_left(addr_b[:self.level_count], level)

        m.d.comb += [
            self.addr_a.eq(addr_a),
            self.addr_b.eq(addr_b),
            self.addr_twiddle.eq(index & twiddle_mask),
        ]

        return m

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


class Butterfly(Elaboratable):
    def __init__(self, sample_shape, twiddle_factor_shape):
        self.sample_shape   = sample_shape
        self.in_a           = Complex(shape=sample_shape)
        self.in_b           = Complex(shape=sample_shape)
        self.out_a          = Complex(shape=sample_shape)
        self.out_b          = Complex(shape=sample_shape)
        self.twiddle_factor = Complex(shape=twiddle_factor_shape)

    def elaborate(self, platform):
        m = Module()

        a = self.in_a
        b = self.in_b * self.twiddle_factor
        b = b.reshape(self.sample_shape)
        m.d.comb += [
            self.out_a.eq((a + b).reshape(self.sample_shape)),
            self.out_b.eq((a - b).reshape(self.sample_shape)),
        ]

        return m


class TwiddleFactors(Elaboratable):
    def __init__(self, fft_size, sample_shape):
        self.fft_size = fft_size

        tf_count = int(fft_size/2)

        def tf(k):
            tf = cmath.exp(-1j * math.tau * k / fft_size)
            m = 2**sample_shape.fraction_bits - 1
            return (round(tf.real*m), round(tf.imag*m))

        twiddle_factors = [tf(k) for k in range(tf_count)]
        tf_real = [x[0] for x in twiddle_factors]
        tf_imag = [x[1] for x in twiddle_factors]
        self.mem_real = Memory(width=len(sample_shape), depth=len(twiddle_factors), init=tf_real)
        self.mem_imag = Memory(width=len(sample_shape), depth=len(twiddle_factors), init=tf_imag)
        self.out   = Complex(shape=sample_shape)
        self.addr  = Signal(range(tf_count))


    def elaborate(self, platform):
        m = Module()
        m.submodules.rd_real = rd_real = self.mem_real.read_port()
        m.submodules.rd_imag = rd_imag = self.mem_imag.read_port()
        m.d.comb += [
            rd_real.addr.eq(self.addr),
            rd_imag.addr.eq(self.addr),
            self.out.real.eq(rd_real.data),
            self.out.imag.eq(rd_imag.data),
        ]
        return m

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
