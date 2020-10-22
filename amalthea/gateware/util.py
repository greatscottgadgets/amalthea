from nmigen import *
from nmigen.back.pysim import Simulator
from nmigen.build import *
from nmigen.cli import main

import unittest

class Serializer(Elaboratable):
    """ Convert a signal into a stream of narrower signals. """
    def __init__(self, *, w_width, r_width):
        if not w_width > r_width:
            raise TypeError(f"Serializer w_width ({w_width}) must be"
                            f"greater than output width ({r_width})")

        if w_width % r_width != 0:
            raise TypeError(f"Serializer w_width ({w_width}) must be"
                            f"an integer multiple of output width ({r_width})")

        self._divisor = int(w_width / r_width)
        self._count   = Signal(range(self._divisor+1))
        self._data    = Signal(w_width)

        self.w_data   = Signal(w_width)
        self.w_rdy    = Signal()
        self.w_en     = Signal()

        self.r_data   = Signal(r_width)
        self.r_rdy    = Signal()
        self.r_en     = Signal()


    def elaborate(self, platform):
        m = Module()

        # Connect the bottom bits of the shift register to the output.
        m.d.comb += self.r_data.eq(self._data[:self.r_data.width])

        # Allow write if the shift register is empty or about to be empty.
        data_empty = self._count == 0
        data_emptying = (self._count == 1) & self.r_en
        m.d.comb += self.w_rdy.eq(data_empty | data_emptying)

        m.d.comb += self.r_rdy.eq(self._count != 0)

        with m.If(self.r_rdy & self.r_en):
            m.d.sync += [
                self._data .eq(self._data >> self.r_data.width),
                self._count.eq(self._count - 1),
            ]

        with m.If(self.w_rdy & self.w_en):
            m.d.sync += [
                self._data.eq(self.w_data),
                self._count.eq(self._divisor),
            ],

        return m


class TestSerializer(unittest.TestCase):
    def test_serializer(self):
        clk = 60e6
        m = Serializer(w_width=32, r_width=8)

        sim = Simulator(m)
        sim.add_clock(1/clk)

        def process():
            data = 0xDDCCBBAA
            yield m.w_data.eq(data)
            yield m.w_en.eq(1)
            yield m.r_en.eq(1)
            yield
            for i in range(10):
                for j in range(4):
                    yield
                    shift = (j*8)
                    mask = (0xff << shift)
                    expected_r_data = (data & mask) >> shift
                    self.assertEqual((yield m.r_data), expected_r_data)

        sim.add_sync_process(process)
        with sim.write_vcd("serializer.vcd", "serializer.gtkw", traces=[]):
            sim.run()


if __name__ == "__main__":
   unittest.main()

