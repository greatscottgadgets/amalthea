from nmigen import *
from nmigen.back.pysim import Simulator
from nmigen.build import *
from nmigen.cli import main
from nmigen.hdl.ast import Past, Rose, Fell

from collections import namedtuple
from math import ceil
from operator import attrgetter
import unittest

class Radio(Elaboratable):
    """ AT86RF215 radio
    """
    def __init__(self):
        self.rst = Signal()
        self.irq = Signal()

        self.sclk = Signal()
        self.sel  = Signal()
        self.mosi = Signal()
        self.miso = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.FSM():
            with m.Case("reset"):
                m.d.sync += self.rst.eq(1)
                # TODO: delay some? or wait till IRQ is stable low?

            with m.Case("wake"):
                # After reset, only IRQS.WAKEUP is enabled.
                # Wait for IRQ to go high to indicate target is ready.
                with m.If(self.irq):
                    m.next = "config"

            with m.Case("config"):
                # TODO: SPI config - IQ mode, freq, bw, rate, tx/rx mode, etc.
                pass

            with m.Case("run"):
                pass

            return m

# TODO: define this upstream somewhere
SYNC_FREQ = 120e6

DelayState = namedtuple("DelayState", "delay next_state")
# From 4.2.5 "SPI Timing" & Table 10-29. "SPI Timing Characteristics"
DELAY_STATES = {
    "SEL_TO_SCLK":  DelayState(ceil(SYNC_FREQ *  50e-9), "SHIFT"), # tSPI_0
    "BYTE_TO_BYTE": DelayState(ceil(SYNC_FREQ * 125e-9), "SHIFT"), # tSPI_5
    "IDLE_TIME":    DelayState(ceil(SYNC_FREQ *  50e-9), "IDLE"),  # tSPI_8
    "SCLK_TO_SEL":  DelayState(ceil(SYNC_FREQ *  45e-9), "END"),   # tSPI_9
}

class RadioSPI(Elaboratable):
    def __init__(self):
        self.start       = Signal()
        self.busy        = Signal()
        self.write       = Signal()
        self.address     = Signal(14)
        self.write_value = Signal(8)
        self.read_value  = Signal(8)

        self.sel  = Signal()
        self.sclk = Signal()
        self.mosi = Signal()
        self.miso = Signal()

        self._delay_counter = Signal(range(max(map(attrgetter("delay"), DELAY_STATES.values()))+1))


    def enter_delay_state(self, m, state):
        m.d.sync += self._delay_counter.eq(DELAY_STATES[state].delay)
        m.next = state

    def elaborate(self, platform):
        m = Module()

        SPI_FREQ = 20e6
        CLKS_PER_HALFBIT = int(SYNC_FREQ // (SPI_FREQ * 2))
        sclk_counter = Signal(range(CLKS_PER_HALFBIT))

        # Shift register for 4.2.3 "Single Access Mode" transaction.
        # (first bit is shifted immediately on start pulse, so -1 here)
        data = Signal(3*8-1)
        bits_remaining = Signal(range(9))
        bytes_remaining = Signal(range(3))

        with m.FSM() as fsm:
            m.d.comb += self.busy.eq(~fsm.ongoing("IDLE"))

            with m.State("IDLE"):
                with m.If(self.start):
                    m.d.sync += [
                        data.eq(Cat(self.write_value, self.address, 0)),
                        self.sel.eq(1),
                        self.sclk.eq(0),
                        self.mosi.eq(self.write),
                        bits_remaining.eq(8),
                        bytes_remaining.eq(2),
                    ]
                    self.enter_delay_state(m, "SEL_TO_SCLK")

            with m.State("SHIFT"):
                m.d.sync += sclk_counter.eq(sclk_counter - 1)

                with m.If(sclk_counter == 0):
                    m.d.sync += self.sclk.eq(~self.sclk)

                    with m.If(self.sclk): # Falling edge: shift MSb out
                        m.d.sync += self.mosi.eq(data[-1])
                        m.d.sync += data.eq(Cat(0, data[:-1]))
                        m.d.sync += bits_remaining.eq(bits_remaining - 1)

                    with m.Else(): # Rising edge: shift data in
                        m.d.sync += self.read_value.eq(Cat(self.miso, self.read_value[:-1]))

                    m.d.sync += sclk_counter.eq(CLKS_PER_HALFBIT-1)

                with m.If(bits_remaining == 0):
                    with m.If(bytes_remaining == 0):
                        # Transaction finished: delay before deasserting chip select.
                        self.enter_delay_state(m, "SCLK_TO_SEL")

                    with m.Else():
                        # Byte finished: reset and delay before transmitting next byte.
                        m.d.sync += bytes_remaining.eq(bytes_remaining - 1)
                        m.d.sync += bits_remaining.eq(8)
                        self.enter_delay_state(m, "BYTE_TO_BYTE")

            with m.State("END"):
                # Deassert chip select and delay before next transaction can start.
                m.d.sync += self.sel.eq(0)
                self.enter_delay_state(m, "IDLE_TIME")


            for state in DELAY_STATES:
                with m.State(state):
                    with m.If(self._delay_counter == 0):
                        m.next = DELAY_STATES[state].next_state
                    with m.Else():
                        m.d.sync += self._delay_counter.eq(self._delay_counter - 1)


        return m

            

class TestRadioSPI(unittest.TestCase):
    def test_radiospi(self):
        m = RadioSPI()

        sim = Simulator(m)
        sim.add_clock(1/SYNC_FREQ)

        def process():
            yield m.address.eq(0x3EAB)
            yield m.write.eq(1)
            yield m.write_value.eq(0x3)
            yield m.start.eq(1)
            while (not (yield m.busy)):
                yield

            yield m.start.eq(0)
            while (yield m.busy):
                yield

        sim.add_sync_process(process)
        with sim.write_vcd("radiospi.vcd", "radiospi.gtkw", traces=[]):
            sim.run()

if __name__ == "__main__":
   unittest.main()

