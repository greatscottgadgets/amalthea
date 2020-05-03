#!/usr/bin/env python3
#
# This file is part of LUNA.
#

import operator
from functools import reduce

from nmigen import Signal, Elaboratable, Module, Cat, ClockDomain, ClockSignal, ResetSignal
from nmigen.lib.cdc import FFSynchronizer

from luna                             import top_level_cli
from luna.gateware.utils.cdc          import synchronize
from luna.gateware.architecture.car   import LunaECP5DomainGenerator
from luna.gateware.interface.spi      import SPIRegisterInterface
from luna.gateware.interface.ulpi     import ULPIRegisterWindow
from luna.gateware.interface.flash    import ECP5ConfigurationFlashInterface
from luna.gateware.interface.psram    import HyperRAMInterface

from luna.apollo.support.selftest     import ApolloSelfTestCase, named_test

#
# Clock frequencies for each of the domains.
# Can be modified to test at faster or slower frequencies.
#
CLOCK_FREQUENCIES = {
    "fast": 60,
    "sync": 60,
    "usb":  60
}


REGISTER_ID             = 1
REGISTER_LEDS           = 2
REGISTER_TARGET_POWER   = 3

REGISTER_USER_IO_DIR    = 4
REGISTER_USER_IO_IN     = 5
REGISTER_USER_IO_OUT    = 6

REGISTER_TARGET_ADDR    = 7
REGISTER_TARGET_VALUE   = 8
REGISTER_TARGET_RXCMD   = 9

REGISTER_HOST_ADDR      = 10
REGISTER_HOST_VALUE     = 11
REGISTER_HOST_RXCMD     = 12

REGISTER_SIDEBAND_ADDR  = 13
REGISTER_SIDEBAND_VALUE = 14
REGISTER_SIDEBAND_RXCMD = 15

REGISTER_RAM_REG_ADDR   = 20
REGISTER_RAM_VALUE      = 21

class InteractiveSelftest(Elaboratable, ApolloSelfTestCase):
    """ Hardware meant to demonstrate use of the Debug Controller's register interface.

    Registers:
        0 -- register/address size auto-negotiation for Apollo
        1 -- gateware ID register (TEST)
        2 -- fpga LEDs
        3 -- target port power control

        4 -- user I/O DDR (1 = out, 0 = in)
        5 -- user I/O input state
        6 -- user I/O output values (used when DDR = 1)

        7 -- target PHY ULPI register address
        8 -- target PHY ULPI register value
        9 -- last target PHY RxCmd

        10 -- host PHY ULPI register address
        11 -- host PHY ULPI register value
        12 -- last host PHY RxCmd

        13 -- sideband PHY ULPI register address
        14 -- sideband PHY ULPI register value
        15 -- last sideband PHY RxCmd

        20 -- HyperRAM register address
        21 -- HyperRAM register value
    """

    def elaborate(self, platform):
        m = Module()

        # Generate our clock domains.
        clocking = LunaECP5DomainGenerator(clock_frequencies=CLOCK_FREQUENCIES)
        m.submodules.clocking = clocking

        # Create a set of registers, and expose them over SPI.
        board_spi = platform.request("debug_spi")
        spi_registers = SPIRegisterInterface(default_read_value=-1)
        m.submodules.spi_registers = spi_registers

        # Simple applet ID register.
        spi_registers.add_read_only_register(REGISTER_ID, read=0x54455354)

        # LED test register.
        led_reg = spi_registers.add_register(REGISTER_LEDS, size=6, name="leds", reset=0b10)
        led_out   = Cat([platform.request("led", i, dir="o") for i in range(0, 6)])
        m.d.comb += led_out.eq(led_reg)

        #
        # Target power test register.
        # Note: these values assume you've populated the correct AP22814 for
        #       your revision (AP22814As for rev0.2+, and AP22814Bs for rev0.1).
        #     bits [1:0]: 0 = power off
        #                 1 = provide A-port VBUS
        #                 2 = pass through target VBUS
        #
        power_test_reg          = Signal(3)
        power_test_write_strobe = Signal()
        power_test_write_value  = Signal(2)
        spi_registers.add_sfr(REGISTER_TARGET_POWER,
            read=power_test_reg,
            write_strobe=power_test_write_strobe,
            write_signal=power_test_write_value
        )

        # Store the values for our enable bits.
        with m.If(power_test_write_strobe):
            m.d.sync += power_test_reg[0:2].eq(power_test_write_value)

        # Decode the enable bits and control the two power supplies.
        power_a_port      = platform.request("power_a_port")
        power_passthrough = platform.request("pass_through_vbus")
        with m.If(power_test_reg[0:2] == 1):
            m.d.comb += [
                power_a_port       .eq(1),
                power_passthrough  .eq(0)
            ]
        with m.Elif(power_test_reg[0:2] == 2):
            m.d.comb += [
                power_a_port       .eq(0),
                power_passthrough  .eq(1)
            ]
        with m.Else():
            m.d.comb += [
                power_a_port       .eq(0),
                power_passthrough  .eq(0)
            ]

        #
        # User IO GPIO registers.
        #

        # Data direction register.
        user_io_dir = spi_registers.add_register(REGISTER_USER_IO_DIR, size=4)

        # Pin (input) state register.
        user_io_in  = Signal(4)
        spi_registers.add_sfr(REGISTER_USER_IO_IN, read=user_io_in)

        # Output value register.
        user_io_out = spi_registers.add_register(REGISTER_USER_IO_OUT, size=4)

        # Grab and connect each of our user-I/O ports our GPIO registers.
        for i in range(4):
            pin = platform.request("user_io", i)
            m.d.comb += [
                pin.oe         .eq(user_io_dir[i]),
                user_io_in[i]  .eq(pin.i),
                pin.o          .eq(user_io_out[i])
            ]


        #
        # ULPI PHY windows
        #
        self.add_ulpi_registers(m, platform,
            ulpi_bus="target_phy",
            register_base=REGISTER_TARGET_ADDR
        )
        self.add_ulpi_registers(m, platform,
            ulpi_bus="host_phy",
            register_base=REGISTER_HOST_ADDR
        )
        self.add_ulpi_registers(m, platform,
            ulpi_bus="sideband_phy",
            register_base=REGISTER_SIDEBAND_ADDR
        )


        #
        # HyperRAM test connections.
        #
        ram_bus = platform.request('ram')
        psram = HyperRAMInterface(bus=ram_bus)
        m.submodules += psram

        psram_address_changed = Signal()
        psram_address = spi_registers.add_register(REGISTER_RAM_REG_ADDR, write_strobe=psram_address_changed)

        spi_registers.add_sfr(REGISTER_RAM_VALUE, read=psram.read_data)

        # Hook up our PSRAM.
        m.d.comb += [
            ram_bus.reset          .eq(0),
            psram.single_page      .eq(0),
            psram.perform_write    .eq(0),
            psram.register_space   .eq(1),
            psram.final_word       .eq(1),
            psram.start_transfer   .eq(psram_address_changed),
            psram.address          .eq(psram_address),
        ]


        #
        # SPI flash passthrough connections.
        #
        flash_sdo = Signal()

        spi_flash_bus = platform.request('spi_flash')
        spi_flash_passthrough = ECP5ConfigurationFlashInterface(bus=spi_flash_bus)

        m.submodules += spi_flash_passthrough
        m.d.comb += [
            spi_flash_passthrough.sck   .eq(board_spi.sck),
            spi_flash_passthrough.sdi   .eq(board_spi.sdi),
            flash_sdo                   .eq(spi_flash_passthrough.sdo),
        ]

        #
        # Synchronize each of our I/O SPI signals, where necessary.
        #
        spi = synchronize(m, board_spi)

        # Select the passthrough or gateware SPI based on our chip-select values.
        gateware_sdo = Signal()
        with m.If(spi_registers.spi.cs):
            m.d.comb += board_spi.sdo.eq(gateware_sdo)
        with m.Else():
            m.d.comb += board_spi.sdo.eq(flash_sdo)

        # Connect our register interface to our board SPI.
        m.d.comb += [
            spi_registers.spi.sck .eq(spi.sck),
            spi_registers.spi.sdi .eq(spi.sdi),
            gateware_sdo          .eq(spi_registers.spi.sdo),
            spi_registers.spi.cs  .eq(spi.cs)
        ]

        return m


    def add_ulpi_registers(self, m, platform, *, ulpi_bus, register_base):
        """ Adds a set of ULPI registers to the active design. """

        target_ulpi      = platform.request(ulpi_bus)

        ulpi_reg_window  = ULPIRegisterWindow()
        m.submodules  += ulpi_reg_window

        m.d.comb += [
            ulpi_reg_window.ulpi_data_in  .eq(target_ulpi.data.i),
            ulpi_reg_window.ulpi_dir      .eq(target_ulpi.dir),
            ulpi_reg_window.ulpi_next     .eq(target_ulpi.nxt),

            target_ulpi.clk      .eq(ClockSignal("usb")),
            target_ulpi.rst      .eq(ResetSignal("usb")),
            target_ulpi.stp      .eq(ulpi_reg_window.ulpi_stop),
            target_ulpi.data.o   .eq(ulpi_reg_window.ulpi_data_out),
            target_ulpi.data.oe  .eq(~target_ulpi.dir)
        ]

        register_address_change  = Signal()
        register_value_change    = Signal()

        # ULPI register address.
        spi_registers = m.submodules.spi_registers
        spi_registers.add_register(register_base + 0,
            write_strobe=register_address_change,
            value_signal=ulpi_reg_window.address,
            size=6
        )
        m.submodules.clocking.stretch_sync_strobe_to_usb(m,
            strobe=register_address_change,
            output=ulpi_reg_window.read_request,
        )

        # ULPI register value.
        spi_registers.add_sfr(register_base + 1,
            read=ulpi_reg_window.read_data,
            write_signal=ulpi_reg_window.write_data,
            write_strobe=register_value_change
        )
        m.submodules.clocking.stretch_sync_strobe_to_usb(m,
            strobe=register_value_change,
            output=ulpi_reg_window.write_request
        )


    def assertPhyRegister(self, phy_register_base: int, register: int, expected_value: int):
        """ Asserts that a PHY register contains a given value.

        Parameters:
            phy_register_base -- The base address of the PHY window in the debug SPI
                                 address range.
            register          -- The PHY register to check.
            value             -- The expected value of the relevant PHY register.
        """

        # Set the address of the ULPI register we're going to read from.
        self.dut.spi.register_write(phy_register_base, register)

        # ... and read back its value.
        actual_value = self.dut.spi.register_read(phy_register_base + 1)

        # Finally, validate it.
        if actual_value != expected_value:
            raise AssertionError(f"PHY register {register} was {actual_value}, not expected {expected_value}")


    def assertPhyPresence(self, register_base: int):
        """ Assertion that fails iff the given PHY isn't detected. """

        # Check the value of our four ID registers, which should
        # read 2404:0900 (vendor: microchip; product: USB3343).
        self.assertPhyRegister(register_base, 0, 0x24)
        self.assertPhyRegister(register_base, 1, 0x04)
        self.assertPhyRegister(register_base, 2, 0x09)
        self.assertPhyRegister(register_base, 3, 0x00)


    def assertHyperRAMRegister(self, address: int, expected_value: int):
        """ Assertion that fails iff a RAM register doesn't hold the expected value. """

        self.dut.spi.register_write(REGISTER_RAM_REG_ADDR, address)
        self.dut.spi.register_write(REGISTER_RAM_REG_ADDR, address)
        actual_value =  self.dut.spi.register_read(REGISTER_RAM_VALUE)

        if actual_value != expected_value:
            raise AssertionError(f"PHY register {address} was {actual_value}, not expected {expected_value}")


    @named_test("Debug module")
    def test_debug_connection(self, dut):
        self.assertRegisterValue(1, 0x54455354)


    @named_test("Host PHY")
    def test_host_phy(self, dut):
        self.assertPhyPresence(REGISTER_HOST_ADDR)


    @named_test("Target PHY")
    def test_target_phy(self, dut):
        self.assertPhyPresence(REGISTER_TARGET_ADDR)


    @named_test("Sideband PHY")
    def test_sideband_phy(self, dut):
        self.assertPhyPresence(REGISTER_SIDEBAND_ADDR)


    @named_test("HyperRAM")
    def test_hyperram(self, dut):
        self.assertHyperRAMRegister(0, 0x0c81)



if __name__ == "__main__":
    tester = top_level_cli(InteractiveSelftest)

    if tester:
        tester.run_tests()

    print()
