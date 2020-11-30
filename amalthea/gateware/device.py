#!/usr/bin/env python3
# pylint: disable=no-member

import os
import sys
import logging
import time
import usb1

import numpy as np

from nmigen                          import *
from nmigen.lib.fifo                 import AsyncFIFO

from usb_protocol.types              import USBRequestType
from usb_protocol.emitters           import DeviceDescriptorCollection

from luna                            import top_level_cli
from luna.usb2                       import *
from luna.gateware.usb.usb2.request  import USBRequestHandler

from .radio                          import IQReceiver, RadioSPI
from .demod                          import CORDICDemod
from .stream                         import IQStream, SampleStream, StreamCombiner

from ..gnuradio.amaltheasource import AmaltheaSource


VENDOR_ID  = 0x16d0
PRODUCT_ID = 0x0f3b

BULK_ENDPOINT_NUMBER = 1
MAX_BULK_PACKET_SIZE = 64 if os.getenv('LUNA_FULL_ONLY') else 512

class RadioSPIRequestHandler(USBRequestHandler):
    """ Read/write radio SPI registers. """

    REQUEST_WRITE_REG = 0

    def __init__(self):
        super(RadioSPIRequestHandler, self).__init__()
        self.spi_start       = Signal()
        self.spi_busy        = Signal()
        self.spi_address     = Signal(14)
        self.spi_write       = Signal()
        self.spi_write_value = Signal(8)

    def elaborate(self, platform):
        m = Module()

        interface         = self.interface
        setup             = self.interface.setup

        m.d.comb += self.spi_write.eq(1) # Only support writes for now
        m.d.sync += self.spi_start.eq(0)

        with m.If(setup.type == USBRequestType.VENDOR):
            with m.FSM():
                with m.State('IDLE'):
                    with m.If(setup.received):
                        with m.Switch(setup.request):
                            with m.Case(self.REQUEST_WRITE_REG):
                                m.d.sync += [
                                    self.spi_address.eq(setup.index[:14]),
                                    self.spi_write_value.eq(setup.value[:8]),
                                    self.spi_start.eq(1),
                                ],
                                m.next = 'WRITE_REG'

                            with m.Default():
                                m.next = 'UNHANDLED'

                with m.State('WRITE_REG'):
                    # Once the receive is complete, respond with an ACK.
                    with m.If(interface.rx_ready_for_response):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                    # If we reach the status stage, send a ZLP.
                    with m.If(interface.status_requested):
                        m.d.comb += self.send_zlp()
                        m.next = 'IDLE'


                with m.State('UNHANDLED'):

                    #
                    # Stall unhandled requests.
                    #
                    with m.If(interface.status_requested | interface.data_requested):
                        m.d.comb += interface.handshakes_out.stall.eq(1)
                        m.next = 'IDLE'

                return m


class Device(Elaboratable):
    """ Amalthea device. """

    def __init__(self):
        self._rx = IQReceiver();
        self._blocks = {}
        self._usb_outputs = []
        self._connections = []
        self._usb_connections = []

    def get_rx(self):
        return self._rx

    def add_block(self, block_id, block):
        self._blocks[block_id] = block
        return block

    def connect(self, source, sink):
        print(f"connect {source} {sink}")
        source_id, source_output = source
        sink_id, sink_input = sink

        source_block = self._blocks[source_id]
        sink_block   = self._blocks[sink_id]
        self._connections.append(sink_block.input.stream_eq(source_block.outputs[source_output]))

    def connect_usb(self, source, sink):
        print(f"connect_usb {source}")
        block_id, output_id = source
        self._usb_outputs.append(self._blocks[block_id].outputs[output_id])
        self._usb_connections.append((len(self._usb_outputs)-1, sink))

    def finalize_usb_connections(self, tb):
        def to_np_type(output):
            if isinstance(output, IQStream):
                return np.complex64
            if isinstance(output, SampleStream):
                return np.float32
            raise TypeError("Unknown stream type")

        signature = list(map(to_np_type, self._usb_outputs))
        self._usb_source = AmaltheaSource(4e6, 2.45e9, signature)
        for conn in self._usb_connections:
            tb.connect((self._usb_source, conn[0]), conn[1])


    def create_descriptors(self):
        """ Create the descriptors we want to use for our device. """

        descriptors = DeviceDescriptorCollection()

        #
        # We'll add the major components of the descriptors we we want.
        # The collection we build here will be necessary to create a standard endpoint.
        #

        # We'll need a device descriptor...
        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = VENDOR_ID
            d.idProduct          = PRODUCT_ID

            d.iManufacturer      = "GSG"
            d.iProduct           = "Amalthea receiver"
            d.iSerialNumber      = "no serial"

            d.bNumConfigurations = 1


        # ... and a description of the USB configuration we'll provide.
        with descriptors.ConfigurationDescriptor() as c:

            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0

                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x80 | BULK_ENDPOINT_NUMBER
                    e.wMaxPacketSize   = MAX_BULK_PACKET_SIZE


        return descriptors


    def elaborate(self, platform):
        m = Module()

        # Generate our domain clocks/resets.
        m.submodules.car = platform.clock_domain_generator()

        # Create our USB device interface...
        ulpi = platform.request("host_phy")
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        control_ep = usb.add_standard_control_endpoint(descriptors)

        # Add our vendor request handler
        handler = DomainRenamer("usb")(RadioSPIRequestHandler())
        control_ep.add_request_handler(handler)

        radio = platform.request("radio")
        m.d.comb += radio.rst.eq(0)

        # Setup the radio SPI interface.
        radio_spi = DomainRenamer("usb")(RadioSPI(clk_freq=60e6))
        m.submodules += radio_spi

        m.d.comb += [
            # Output pins
            radio.sel              .eq(radio_spi.sel),
            radio.clk              .eq(radio_spi.clk),
            radio.copi             .eq(radio_spi.copi),

            # Input pins
            radio_spi.cipo         .eq(radio.cipo),

            # Vendor request handler connections
            radio_spi.start        .eq(handler.spi_start),
            handler.spi_busy       .eq(radio_spi.busy),
            radio_spi.address      .eq(handler.spi_address),
            radio_spi.write        .eq(handler.spi_write),
            radio_spi.write_value  .eq(handler.spi_write_value),
        ]

        # Create radio clock domain
        m.domains.radio = ClockDomain()
        m.d.comb += [
            ClockSignal("radio").eq(radio.rxclk),
            ResetSignal("radio").eq(ResetSignal()),
        ]

        # Get IQ samples.
        iq_rx = self.get_rx()
        m.d.comb += iq_rx.rxd.eq(radio.rxd24)

        #
        m.submodules += map(DomainRenamer("radio"), self._blocks.values())
        m.d.comb += self._connections

        combined = StreamCombiner(
            streams=self._usb_outputs,
            domain="radio",
        )
        m.submodules += combined

        payload = combined.output.payload
        usb_data = Cat(
            # Pad each 13-bit value to 16-bits for now.
            payload.word_select(i, 13).shift_left(3) for i in range(int(len(payload)/13))
        )
        assert (len(usb_data) % 8) == 0, f"{len(usb_data)}"


        # Add a stream endpoint to our device.
        stream_ep = USBMultibyteStreamInEndpoint(
            byte_width=int(len(usb_data)/8),
            endpoint_number=BULK_ENDPOINT_NUMBER,
            max_packet_size=MAX_BULK_PACKET_SIZE
        )
        usb.add_endpoint(stream_ep)

        # Connect our device as a high speed device by default.
        m.d.comb += [
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(1 if os.getenv('LUNA_FULL_ONLY') else 0),
        ]

        # Connect up the IQ receiver to the USB stream, via a small FIFO.
        fifo  = AsyncFIFO(width=len(usb_data), depth=128, r_domain="usb", w_domain="radio")
        m.submodules += fifo
        m.d.comb += [
            combined.output.ready      .eq(fifo.w_rdy),
            fifo.w_en                  .eq(combined.output.valid),
            fifo.w_data                .eq(usb_data),
            fifo.r_en                  .eq(stream_ep.stream.ready),
            stream_ep.stream.valid     .eq(fifo.r_rdy),
            stream_ep.stream.payload   .eq(fifo.r_data),
            stream_ep.stream.last      .eq(0),
        ]

        # Debug LEDs.
        led0 = platform.request("led", 0)
        m.d.radio += led0.eq(iq_rx.outputs[0].valid)
        led1 = platform.request("led", 1)
        m.d.usb += led1.eq(stream_ep.stream.valid)
        led2 = platform.request("led", 2)
        m.d.radio += led2.eq(fifo.w_rdy)


        return m


if __name__ == "__main__":
    device = top_level_cli(Device)

