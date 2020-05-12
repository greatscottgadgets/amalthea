#
# This file is part of Amalthea.
#

import os

from nmigen.build import Resource, Subsignal, Pins, PinsN, Attrs, Clock, DiffPairs, Connector
from nmigen.vendor.lattice_ecp5 import LatticeECP5Platform
from luna.gateware.architecture.car import LunaECP5DomainGenerator


__all__ = ["AmaltheaPlatformRev0D1"]

#
# Note that r0.2+ have D+/D- swapped to avoid having to cross D+/D- in routing.
#
# This is supported by a PHY feature that allows you to swap pins 13 + 14.
#

def ULPIResource(name, data_sites, clk_site, dir_site, nxt_site, stp_site, reset_site):
    """ Generates a set of resources for a ULPI-connected USB PHY. """

    return Resource(name, 0,
        Subsignal("data",  Pins(data_sites,  dir="io")),
        Subsignal("clk",   Pins(clk_site,    dir="o" )),
        Subsignal("dir",   Pins(dir_site,    dir="i" )),
        Subsignal("nxt",   Pins(nxt_site,    dir="i" )),
        Subsignal("stp",   Pins(stp_site,    dir="o" )),
        Subsignal("rst",   PinsN(reset_site, dir="o" )),
        Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")
    )


class AmaltheaPlatformRev0D1(LatticeECP5Platform):
    """ Board description for the pre-release r0.1 revision of LUNA. """

    name        = "Amalthea r0.1"

    device      = "LFE5U-12F"
    package     = "BG256"
    speed       = os.getenv("LUNA_SPEED_GRADE", "8")

    default_clk = "clk_60MHz"

    # Provide the type that'll be used to create our clock domains.
    clock_domain_generator = LunaECP5DomainGenerator

    #
    # Default clock frequencies for each of our clock domains.
    #
    # Different revisions have different FPGA speed grades, and thus the
    # default frequencies will vary.
    #
    DEFAULT_CLOCK_FREQUENCIES_MHZ = {
        "fast": 240,
        "sync": 120,
        "usb":  60
    }

    #
    # Preferred DRAM bus I/O (de)-skewing constants.
    #
    ram_timings = dict(
        clock_skew = 64
    )

    # Provides any platform-specific ULPI registers necessary.
    # This is the spot to put any platform-specific vendor registers that need
    # to be written.
    ulpi_extra_registers = {
        0x39: 0b000110 # USB3343: swap D+ and D- to match the LUNA boards
    }



    #
    # I/O resources.
    #
    resources   = [

        # Primary, discrete 60MHz oscillator.
        Resource("clk_60MHz", 0, Pins("A7", dir="i"),
            Clock(60e6), Attrs(IO_TYPE="LVCMOS33")),

        # Connection to our SPI flash; can be used to work with the flash
        # from e.g. a bootloader.
        Resource("spi_flash", 0,

            # SCK is on pin 9; but doesn't have a traditional I/O buffer.
            # Instead, we'll need to drive a clock into a USRMCLK instance.
            # See interfaces/flash.py for more information.
            Subsignal("sdi",  Pins("T8",  dir="o")),
            Subsignal("sdo",  Pins("T7",  dir="i")),

            # In r0.1, the chip select line can either be driven by the FPGA
            # or by the Debug Controller. Accordingly, we'll mark the line as
            # bidirectional, and let the user decide.
            Subsignal("cs",   PinsN("N8", dir="io")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # UART connected to the debug controller; can be routed to a host via CDC-ACM.
        Resource("uart", 0,
            Subsignal("rx",   Pins("R14", dir="i")),
            Subsignal("tx",   Pins("T14", dir="o")),
            Attrs(IO_TYPE="LVCMOS33")
        ),


        # SPI bus connected to the debug controller, for simple register exchanges.
        # Note that the Debug Controller is the master on this bus.
        Resource("debug_spi", 0,
            Subsignal("sck",  Pins( "R13", dir="i")),
            Subsignal("sdi",  Pins( "P13", dir="i")),
            Subsignal("sdo",  Pins( "P11", dir="o")),
            Subsignal("cs",   PinsN("T13", dir="i")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # FPGA-connected LEDs.
        Resource("led",  5, PinsN("P15", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("led",  4, PinsN("N16", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("led",  3, PinsN("M15", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("led",  2, PinsN("M16", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("led",  1, PinsN("L15", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("led",  0, PinsN("L16", dir="o"), Attrs(IO_TYPE="LVCMOS33")),

        # USB PHYs
        ULPIResource("sideband_phy",
            data_sites="R2 R1 P2 P1 N1 M2 M1 L2", clk_site="R4",
            dir_site="T3", nxt_site="T2", stp_site="T4", reset_site="R3"),
        ULPIResource("host_phy",
            data_sites="G2 G1 F2 F1 E1 D1 C1 C2", clk_site="K2",
            dir_site="J1", nxt_site="H2", stp_site="J2", reset_site="K1"),

        # HyperRAM (1V8 domain).
        Resource("ram", 0,
            # Note: our clock uses the pseudo-differential I/O present on the top tiles.
            # This requires a recent version of trellis+nextpnr. If your build complains
            # that LVCMOS18D is an invalid I/O type, you'll need to upgrade.
            Subsignal("clk",   DiffPairs("B14", "A15", dir="o"), Attrs(IO_TYPE="LVCMOS18D")),
            Subsignal("dq",    Pins("A11 B10 B12 A12 B11 A10 B9 A9", dir="io")),
            Subsignal("rwds",  Pins( "A13", dir="io")),
            Subsignal("cs",    PinsN("A14", dir="o")),
            Subsignal("reset", PinsN("B13", dir="o")),
            Attrs(IO_TYPE="LVCMOS18", SLEWRATE="FAST")
        ),

        # Radio.
        Resource("radio", 0,
            Subsignal("rst",   PinsN("C14", dir="o")),

            Subsignal("sclk",  Pins( "K14", dir="o")),
            Subsignal("sel",   PinsN("E16", dir="o")),
            Subsignal("mosi",  Pins( "F16", dir="o")),
            Subsignal("miso",  Pins( "G16", dir="i")),

            Subsignal("irq",   Pins( "F15", dir="i")),

            Subsignal("rxclk", DiffPairs("J16", "J15", dir="i"), Attrs(IO_TYPE="LVDS", DIFFRESISTOR="100", PULLMODE="UP")),
            Subsignal("rxd09", DiffPairs("D16", "E15", dir="i"), Attrs(IO_TYPE="LVDS", DIFFRESISTOR="100")),
            Subsignal("rxd24", DiffPairs("K16", "K15", dir="i"), Attrs(IO_TYPE="LVDS", DIFFRESISTOR="100")),

            Subsignal("txclk", DiffPairs("B16", "B15", dir="o"), Attrs(IO_TYPE="LVCMOS33D", DRIVE="4")),
            Subsignal("txd",   DiffPairs("C16", "C15", dir="o"), Attrs(IO_TYPE="LVCMOS33D", DRIVE="4")),
            Attrs(IO_TYPE="LVCMOS33"),
        ),

        # User I/O connections.
        # TODO: Update these for io0+/- & io1+/-
        Resource("user_io", 0, Pins("A5", dir="io"), Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")),
        Resource("user_io", 1, Pins("A4", dir="io"), Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")),
        Resource("user_io", 2, Pins("A3", dir="io"), Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")),
        Resource("user_io", 3, Pins("A2", dir="io"), Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")),
    ]

    connectors = [

        # User I/O connector.
        Connector("user_io", 0, """
            A5  -  A2
            A4  -  A3
        """)

    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            'ecppack_opts': '--compress --freq 38.8'
        }

        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)


    def toolchain_program(self, products, name):
        """ Programs the relevant LUNA board via its sideband connection. """

        from luna.apollo import ApolloDebugger
        from luna.apollo.ecp5 import ECP5_JTAGProgrammer

        # Create our connection to the debug module.
        debugger = ApolloDebugger()

        # Grab our generated bitstream, and upload it to the FPGA.
        bitstream =  products.get("{}.bit".format(name))
        with debugger.jtag as jtag:
            programmer = ECP5_JTAGProgrammer(jtag)
            programmer.configure(bitstream)


    def toolchain_flash(self, products, name="top"):
        """ Programs the LUNA board's flash via its sideband connection. """

        from luna.apollo import ApolloDebugger
        from luna.apollo.flash import ensure_flash_gateware_loaded

        # Create our connection to the debug module.
        debugger = ApolloDebugger()
        ensure_flash_gateware_loaded(debugger, platform=self.__class__())

        # Grab our generated bitstream, and upload it to the .
        bitstream =  products.get("{}.bit".format(name))
        with debugger.flash as flash:
            flash.program(bitstream)

        debugger.soft_reset()


    def toolchain_erase(self):
        """ Erases the LUNA board's flash. """

        from luna.apollo import ApolloDebugger
        from luna.apollo.flash import ensure_flash_gateware_loaded

        # Create our connection to the debug module.
        debugger = ApolloDebugger()
        ensure_flash_gateware_loaded(debugger, platform=self.__class__())

        with debugger.flash as flash:
            flash.erase()

        debugger.soft_reset()
