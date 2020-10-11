from nmigen import *
from nmigen.back.pysim import Simulator
from nmigen.build import *
from nmigen.cli import main
from nmigen.hdl.ast import Past, Rose, Fell

from collections import namedtuple
from math import ceil
from operator import attrgetter
import unittest

from .stream import IQStream

class Radio(Elaboratable):
    """ AT86RF215 radio
    """
    def __init__(self):
        self.rst = Signal()
        self.irq = Signal()

        self.clk  = Signal()
        self.sel  = Signal()
        self.copi = Signal()
        self.cipo = Signal()

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


DelayState = namedtuple("DelayState", "delay next_state")

class RadioSPI(Elaboratable):
    def __init__(self, clk_freq):
        self.start       = Signal()
        self.busy        = Signal()
        self.write       = Signal()
        self.address     = Signal(14)
        self.write_value = Signal(8)
        self.read_value  = Signal(8)

        self.sel  = Signal()
        self.clk  = Signal()
        self.copi = Signal()
        self.cipo = Signal()

        self._clk_freq = clk_freq

        # From 4.2.5 "SPI Timing" & Table 10-29. "SPI Timing Characteristics"
        self._delay_states = {
            "SEL_TO_SCLK":  DelayState(ceil(clk_freq *  50e-9), "SHIFT"), # tSPI_0
            "BYTE_TO_BYTE": DelayState(ceil(clk_freq * 125e-9), "SHIFT"), # tSPI_5
            "IDLE_TIME":    DelayState(ceil(clk_freq *  50e-9), "IDLE"),  # tSPI_8
            "SCLK_TO_SEL":  DelayState(ceil(clk_freq *  45e-9), "END"),   # tSPI_9
        }

        self._delay_counter = Signal(range(max(map(attrgetter("delay"), self._delay_states.values()))+1))


    def enter_delay_state(self, m, state):
        m.d.sync += self._delay_counter.eq(self._delay_states[state].delay)
        m.next = state

    def elaborate(self, platform):
        m = Module()

        SPI_FREQ = 15e6
        assert (self._clk_freq / 2) % SPI_FREQ == 0.0
        CLKS_PER_HALFBIT = int(self._clk_freq // (SPI_FREQ * 2))
        assert CLKS_PER_HALFBIT > 0
        clk_counter = Signal(range(CLKS_PER_HALFBIT))

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
                        self.clk.eq(0),
                        self.copi.eq(self.write),
                        bits_remaining.eq(8),
                        bytes_remaining.eq(2),
                    ]
                    self.enter_delay_state(m, "SEL_TO_SCLK")

            with m.State("SHIFT"):
                m.d.sync += clk_counter.eq(clk_counter - 1)

                with m.If(clk_counter == 0):
                    m.d.sync += self.clk.eq(~self.clk)

                    with m.If(self.clk): # Rising edge, shift some data.
                        m.d.sync += self.copi.eq(data[-1])
                        m.d.sync += data.eq(Cat(0, data[:-1]))
                        m.d.sync += bits_remaining.eq(bits_remaining - 1)
                        m.d.sync += self.read_value.eq(Cat(self.cipo, self.read_value[:-1]))

                    m.d.sync += clk_counter.eq(CLKS_PER_HALFBIT-1)

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


            for state in self._delay_states:
                with m.State(state):
                    with m.If(self._delay_counter == 0):
                        m.next = self._delay_states[state].next_state
                    with m.Else():
                        m.d.sync += self._delay_counter.eq(self._delay_counter - 1)


        return m

            
class TestRadioSPI(unittest.TestCase):
    def test_radiospi(self):
        clk = 60e6
        m = RadioSPI(clk_freq=clk)

        sim = Simulator(m)
        sim.add_clock(1/clk)

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

I_SYNC = 0b10
Q_SYNC = 0b01

class IQReceiver(Elaboratable):
    def __init__(self):
        self.rxd    = Signal()
        self.output = IQStream()

    def elaborate(self, platform):
        m = Module()

        rxd_delay = Signal()
        data      = Signal(2)
        i_sample  = Signal(signed(14))
        q_sample  = Signal(signed(14))
        m.d.comb += [
            self.output.payload.eq(
                Cat(i_sample[1:], q_sample[1:]),
            ),
            self.output.last.eq(0),
        ]

        m.submodules += [
            Instance("DELAYG",
                p_DEL_MODE="SCLK_CENTERED",
                i_A=self.rxd,
                o_Z=rxd_delay,
            ),
            Instance("IDDRX1F",
                i_D=rxd_delay,
                i_SCLK=ClockSignal(),
                i_RST=ResetSignal(),
                o_Q0=data[1],
                o_Q1=data[0],
            ),
        ]

        data_count = Signal(3)
        m.d.sync += self.output.valid.eq(0)
        with m.FSM() as fsm:
            with m.State("I_SYNC"):
                with m.If(data == I_SYNC):
                    m.next = "I_DATA"
                    m.d.sync += [
                        data_count.eq(0),
                    ]

            with m.State("I_DATA"):
                with m.If(data_count == 6):
                    m.next = "Q_SYNC"

                m.d.sync += [
                    i_sample.eq(Cat(data, i_sample)),
                    data_count.eq(data_count + 1)
                ]

            with m.State("Q_SYNC"):
                with m.If(data == Q_SYNC):
                    m.next = "Q_DATA"
                    m.d.sync += [
                        data_count.eq(0),
                    ]
                with m.Else():
                    m.next = "I_SYNC"

            with m.State("Q_DATA"):
                with m.If(data_count == 6):
                    m.d.sync += self.output.valid.eq(1)
                    m.next = "I_SYNC"

                m.d.sync += [
                    q_sample.eq(Cat(data, q_sample)),
                    data_count.eq(data_count + 1)
                ]


            return m


if __name__ == "__main__":
   unittest.main()

