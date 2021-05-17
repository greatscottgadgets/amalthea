from nmigen import *
from nmigen.sim import Simulator
from .util import variable_rotate_left
import unittest

class FFT(Elaboratable):
    pass


class AddressGenerator(Elaboratable):
    def __init__(self, level_count, butterfly_count):
        self.level_count = level_count
        self.butterfly_count = butterfly_count

        self.done         = Signal()
        self.addr_a       = Signal(range(butterfly_count*2))
        self.addr_b       = Signal(range(butterfly_count*2))
        self.addr_twiddle = Signal(range(level_count))

    def elaborate(self, platform):
        m = Module()

        level        = Signal(range(self.level_count))
        index        = Signal(range(self.butterfly_count))
        twiddle_mask = Signal.like(level)

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
            for i in range(5*16):
                self.assertEqual(((yield m.addr_a), (yield m.addr_b)), expected_addrs[i])
                yield

        sim.add_sync_process(process)
        with sim.write_vcd("agu.vcd", "agu.gtkw", traces=[]):
            sim.run()

if __name__ == "__main__":
    unittest.main()
