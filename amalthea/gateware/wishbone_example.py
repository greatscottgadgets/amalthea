from nmigen import *
from nmigen.sim import *
from nmigen_soc.wishbone import Interface
import unittest

from .stream import SampleStream

SAMPLE_WIDTH = 16

class WishboneCounter(Elaboratable, Interface):
    def __init__(self):
        Interface.__init__(self, data_width=SAMPLE_WIDTH, granularity=SAMPLE_WIDTH, addr_width=0)


    def elaborate(self, platform):
        m = Module()

        counter = Signal(SAMPLE_WIDTH)
        m.d.comb += self.dat_w.eq(counter)

        with m.FSM() as fsm:
            with m.State("START"):
                m.d.sync += [
                    self.cyc.eq(1),
                    self.stb.eq(1),
                ]
                m.next = "WAIT_ACK"

            with m.State("WAIT_ACK"):
                with m.If(self.ack):
                    m.d.sync += [
                        self.cyc.eq(0),
                        self.stb.eq(0),
                        counter.eq(counter + 1),
                    ]
                    m.next = "START"

            with m.State("END"):
                m.next = "START"

        return m

class StreamAdapter(Elaboratable):
    def __init__(self, interface):
        self.interface = interface
        self.outputs = [SampleStream(SAMPLE_WIDTH)]

    def elaborate(self, platform):
        m = Module()

        out = self.outputs[0]

        m.d.comb += [
            self.interface.ack.eq(out.ready),
            out.valid.eq(self.interface.cyc & self.interface.stb),
            out.payload.eq(self.interface.dat_w),
        ]

        return m


class TestWishboneCounter(unittest.TestCase):
    def test_wishbonecounter(self):
        counter = WishboneCounter()

        sim = Simulator(counter)
        sim.add_clock(1/160e6)

        def process():
            for _ in range(50):
                yield counter.ack.eq(counter.cyc & counter.stb)
                yield

        sim.add_sync_process(process)
        with sim.write_vcd("wishbone-counter.vcd", "wishbone-counter.gtkw", traces=[]):
            sim.run()


if __name__ == "__main__":
    unittest.main()

