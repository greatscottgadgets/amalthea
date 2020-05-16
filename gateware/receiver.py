#!/usr/bin/env python3
# pylint: disable=no-member
#
# This file is part of LUNA.
#

import os
import sys
import logging
import time

import usb1

from nmigen                          import *
from usb_protocol.types              import USBRequestType
from usb_protocol.emitters           import DeviceDescriptorCollection

from luna                            import top_level_cli
from luna.gateware.usb.usb2.device   import USBDevice
from luna.gateware.usb.usb2.endpoint import USBStreamInEndpoint
from luna.gateware.usb.usb2.request  import USBRequestHandler

from radio                           import RadioSPI


VENDOR_ID  = 0x16d0
PRODUCT_ID = 0x0f3b

BULK_ENDPOINT_NUMBER = 1
MAX_BULK_PACKET_SIZE = 64 if os.getenv('LUNA_FULL_ONLY') else 512

# Set the total amount of data to be used in our speed test.
TEST_DATA_SIZE = 1 * 1024 * 1024
TEST_TRANSFER_SIZE = 16 * 1024

# Size of the host-size "transfer queue" -- this is effectively the number of async transfers we'll
# have scheduled at a given time.
TRANSFER_QUEUE_DEPTH = 16

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


class USBInSpeedTestDevice(Elaboratable):
    """ Simple device that sends data to the host as fast as hardware can.

    This is paired with the python code below to evaluate LUNA throughput.
    """

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

        radio = platform.request("radio")
        m.d.comb += radio.rst.eq(0)

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

        radio_spi = DomainRenamer("usb")(RadioSPI(clk_freq=60e6))
        m.submodules += radio_spi

        m.d.comb += [
            # Output pins
            radio.sel              .eq(radio_spi.sel),
            radio.sclk             .eq(radio_spi.sclk),
            radio.mosi             .eq(radio_spi.mosi),

            # Input pins
            radio_spi.miso         .eq(radio.miso),

            # Vendor request handler connections
            radio_spi.start        .eq(handler.spi_start),
            handler.spi_busy       .eq(radio_spi.busy),
            radio_spi.address      .eq(handler.spi_address),
            radio_spi.write        .eq(handler.spi_write),
            radio_spi.write_value  .eq(handler.spi_write_value),
        ]

        # Add a stream endpoint to our device.
        stream_ep = USBStreamInEndpoint(
            endpoint_number=BULK_ENDPOINT_NUMBER,
            max_packet_size=MAX_BULK_PACKET_SIZE
        )
        usb.add_endpoint(stream_ep)

        # Send entirely zeroes, as fast as we can.
        m.d.comb += [
            stream_ep.stream.valid    .eq(1),
            stream_ep.stream.payload  .eq(0)
        ]

        # Connect our device as a high speed device by default.
        m.d.comb += [
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(1 if os.getenv('LUNA_FULL_ONLY') else 0),
        ]

        return m


def run_speed_test():
    """ Runs a simple speed test, and reports throughput. """

    total_data_exchanged = 0
    failed_out = False

    _messages = {
        1: "error'd out",
        2: "timed out",
        3: "was prematurely cancelled",
        4: "was stalled",
        5: "lost the device it was connected to",
        6: "sent more data than expected."
    }

    def _should_terminate():
        """ Returns true iff our test should terminate. """
        return (total_data_exchanged > TEST_DATA_SIZE) or failed_out


    def _transfer_completed(transfer: usb1.USBTransfer):
        """ Callback executed when an async transfer completes. """
        nonlocal total_data_exchanged, failed_out

        status = transfer.getStatus()

        # If the transfer completed.
        if status in (usb1.TRANSFER_COMPLETED,):

            # Count the data exchanged in this packet...
            total_data_exchanged += transfer.getActualLength()

            # ... and if we should terminate, abort.
            if _should_terminate():
                return

            # Otherwise, re-submit the transfer.
            transfer.submit()

        else:
            failed_out = status



    with usb1.USBContext() as context:

        # Grab a reference to our device...
        device = context.openByVendorIDAndProductID(0x16d0, 0x0f3b)

        # ... and claim its bulk interface.
        device.claimInterface(0)

        # 24 -> TXPREP
        device.controlWrite(usb1.REQUEST_TYPE_VENDOR, 0, 0x3, 0x0203, [])

        # 24 -> RX
        device.controlWrite(usb1.REQUEST_TYPE_VENDOR, 0, 0x5, 0x0203, [])

        return
        # Submit a set of transfers to perform async comms with.
        active_transfers = []
        for _ in range(TRANSFER_QUEUE_DEPTH):

            # Allocate the transfer...
            transfer = device.getTransfer()
            transfer.setBulk(0x80 | BULK_ENDPOINT_NUMBER, TEST_TRANSFER_SIZE, callback=_transfer_completed, timeout=1000)

            # ... and store it.
            active_transfers.append(transfer)


        # Start our benchmark timer.
        start_time = time.time()

        # Submit our transfers all at once.
        #for transfer in active_transfers:
        #    transfer.submit()

        # Run our transfers until we get enough data.
        while not _should_terminate():
            context.handleEvents()

        # Figure out how long this took us.
        end_time = time.time()
        elapsed = end_time - start_time

        # Cancel all of our active transfers.
        for transfer in active_transfers:
            if transfer.isSubmitted():
                transfer.cancel()

        # If we failed out; indicate it.
        if (failed_out):
            logging.error(f"Test failed because a transfer {_messages[failed_out]}.")
            sys.exit(failed_out)


        bytes_per_second = total_data_exchanged / elapsed
        logging.warning(f"Exchanged {total_data_exchanged / 1000000}MB total at {bytes_per_second / 1000000}MB/s.")


if __name__ == "__main__":
    device = top_level_cli(USBInSpeedTestDevice)

    logging.warning("Giving the device time to connect...")
    time.sleep(10)

    if device is not None:
        logging.warning(f"Starting bulk in speed test.")
        run_speed_test()


