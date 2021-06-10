#!/usr/bin/env python3
# pylint: disable=no-member

from nmigen                          import *

from luna                            import top_level_cli
from luna.usb2                       import *
from luna.gateware.usb.devices.ila   import USBIntegratedLogicAnalyzer
from luna.gateware.usb.devices.ila   import USBIntegratedLogicAnalyzerFrontend

from ..fft import FFT
from ..types.complex import ComplexConst
from ..types.fixed_point import Q


class Device(Elaboratable):
    """ Amalthea device. """

    def __init__(self):
        self.fft = FFT(32, Q(1,10))
        self.in_a = Signal.like(self.fft._butterfly.in_a.value())
        self.in_b = Signal.like(self.fft._butterfly.in_b.value())
        self.out_a = Signal.like(self.fft._butterfly.out_a.value())
        self.out_b = Signal.like(self.fft._butterfly.out_b.value())
        self.ila = USBIntegratedLogicAnalyzer(
            domain="usb",
            signals=[
                self.fft.start,
                self.fft._addr_gen.addr_a,
                self.fft._addr_gen.addr_b,
                self.fft._addr_gen.addr_twiddle,
                self.in_a,
                self.in_b,
                self.out_a,
                self.out_b,
                self.fft.read_addr,
                self.fft.read_data,
            ],
            sample_depth=512
        )

    def interactive_display(self):
        frontend = USBIntegratedLogicAnalyzerFrontend(ila=self.ila)
        frontend.interactive_display()

    def elaborate(self, platform):
        m = Module()

        # init samples for FFT
        input = [1+0j]*16 + [-1+0j]*16
        data = list(map(lambda x: ComplexConst(self.fft.internal_shape, x).value(), input))
        rev = lambda i: int('{:05b}'.format(i)[::-1], 2)
        self.fft.mem.init = [data[rev(i)] for i in range(len(data))]

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        m.submodules.ila = self.ila
        m.submodules.fft = DomainRenamer("usb")(self.fft)

        start = Signal()
        m.d.comb += [
            self.fft.start.eq(start),
            self.ila.trigger.eq(start),
        ]

        read_counter = Signal(range(self.fft.fft_size))
        m.d.comb += [
            self.in_a .eq(self.fft._butterfly.in_a.value()),
            self.in_b .eq(self.fft._butterfly.in_b.value()),
            self.out_a.eq(self.fft._butterfly.out_a.value()),
            self.out_b.eq(self.fft._butterfly.out_b.value()),
            self.fft.read_addr.eq(read_counter),
        ]

        with m.FSM() as fsm:
            m.d.comb += start.eq(fsm.ongoing("START"))
            with m.State("START"):
                with m.If(self.fft.done == 0):
                    m.next = "RUN"

            with m.State("RUN"):
                with m.If(self.fft.done):
                    m.next = "READ"

            with m.State("READ"):
                m.d.usb += read_counter.eq(read_counter+1)
                with m.If(read_counter == self.fft.fft_size-1):
                    m.next = "DONE"

            with m.State("DONE"):
                pass



        return m


if __name__ == "__main__":
    device = top_level_cli(Device)
    device.interactive_display()

