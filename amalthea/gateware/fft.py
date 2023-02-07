from amaranth import *
from amaranth.hdl.dsl import _ModuleBuilderSubmodules
from amaranth.sim import Simulator, Settle
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


if __name__ == "__main__":
    unittest.main()
